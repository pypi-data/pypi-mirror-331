from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from pydantic import BaseModel, model_validator
from typing import List, Dict, Any
from datetime import datetime
import os
import aiosqlite
from aac_init.control_engine.controller import controller, context_cache
from loguru import logger
import asyncio

app = FastAPI()

DATA_PATH = f"/data/{os.getenv('FABRIC_NAME')}/fabric_data/"
DB_PATH = f"/data/{os.getenv('FABRIC_NAME')}/api/task_records.db"
OUTPUT_DIR = f"/data/{os.getenv('FABRIC_NAME')}/logs/"
APP_LOG_DIR = f"/data/{os.getenv('FABRIC_NAME')}/api/"


# if DATA_PATH not exists, create it
if not os.path.exists(DATA_PATH):
    os.makedirs(DATA_PATH)

# if DB_PATH not exists, create it
if not os.path.exists(os.path.dirname(DB_PATH)):
    os.makedirs(os.path.dirname(DB_PATH))

if not os.path.exists(APP_LOG_DIR):
    os.makedirs(APP_LOG_DIR)

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path

    async def _connect(self):
        return await aiosqlite.connect(self.db_path)

    async def init_db(self):
        conn = await self._connect()
        cursor = await conn.cursor()
        await cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                task_details TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                completion_status TEXT DEFAULT 'in progress',
                status TEXT DEFAULT '',
                details TEXT DEFAULT ''
            )
        ''')
        await conn.commit()
        await conn.close()

    async def insert_task_record(self, user_id, task_details):
        conn = await self._connect()
        cursor = await conn.cursor()
        await cursor.execute('INSERT INTO tasks (user_id, task_details, completion_status, status) VALUES (?, ?, ?, ?)',
                             (user_id, task_details, 'in progress', 'in progress'))
        await conn.commit()

        await cursor.execute('DELETE FROM tasks WHERE id NOT IN (SELECT id FROM tasks ORDER BY timestamp DESC LIMIT 100)')
        await conn.commit()
        await conn.close()

    async def update_task_status(self, user_id, status, details=""):
        conn = await self._connect()
        cursor = await conn.cursor()
        await cursor.execute('UPDATE tasks SET status = ?, details = ?, completion_status = "completed" WHERE user_id = ? AND completion_status = "in progress"',
                             (status, details, user_id))
        await conn.commit()
        await conn.close()


db = Database(DB_PATH)
# set log path
logger.add(f"{APP_LOG_DIR}force_api.log", rotation="500 MB")


@app.on_event("startup")
async def startup_db():
    await db.init_db()
    logger.info("Database initialized")


class Task(BaseModel):
    alias: str = None
    project: str = None
    product: str = None
    operations: List[str]
    params: Dict[str, Any] = {}

    @model_validator(mode='before')
    def check_alias_or_project_product(cls, values):
        alias = values.get("alias")
        project = values.get("project")
        product = values.get("product")

        if alias and (project or product):
            raise ValueError("Only one of alias or project/product should be provided.")

        if not alias and not (project and product):
            raise ValueError("Either alias or project/product should be provided.")

        return values


class RunTaskRequest(BaseModel):
    user_id: str
    tasks: List[Task]


async def task_completion_callback(task_group, output_dir, result, user_id):
    logger.info(f"Task completed for {user_id}: {result}")
    for res in result:
        status = res.get("status")
        details = res.get("details", "")
        if not status:
            await db.update_task_status(user_id, "failed", details)
            break
    else:
        await db.update_task_status(user_id, "success")


async def execute_tasks(task_groups, output_dir, user_id):
    results = await asyncio.to_thread(controller.execute, task_groups, output_dir)
    await task_completion_callback(task_groups, output_dir, results, user_id)
    return results


@app.post("/run_tasks")
async def run_tasks(request: RunTaskRequest, background_tasks: BackgroundTasks):
    if context_cache.get("is_running"):
        raise HTTPException(status_code=400, detail="Task execution is already in progress.")

    user_id = request.user_id
    tasks = request.tasks
    context_cache.set("is_running", True)
    context_cache.set("current_user", user_id)

    task_groups = []
    for task in tasks:
        alias = task.alias
        project = task.project
        product = task.product
        operations = task.operations
        params = task.params
        params.update({"data_path": DATA_PATH})

        if alias:
            project, product = controller.resolve_alias(alias)

        ordered_operations = controller.resolve_execution_order(operations, project, product)
        task_groups.append({
            "project": project,
            "product": product,
            "operations": ordered_operations,
            "alias": alias,
            "params": params,
        })

    task_details = str(task_groups)
    await db.insert_task_record(user_id, task_details)

    current_datetime = datetime.now().strftime("%Y%m%d-%H%M%S")
    fabric_name = os.path.basename(os.path.normpath(DATA_PATH))
    base_dir_template = "aac_init_{fabric_name}_{user}_" + f"working_dir_{current_datetime}"
    output_base_dir_template = os.path.join(os.getcwd(), base_dir_template)
    output_dir = output_base_dir_template.format(fabric_name=fabric_name, user=user_id)
    output_dir = os.path.join(OUTPUT_DIR, output_dir)

    # if OUTPUT_DIR not exists, create it
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    background_tasks.add_task(execute_tasks, task_groups, output_dir, user_id)
    logger.info(f"Task execution started for {user_id}.")
    return {"message": "Task execution started."}


@app.get("/my-progress")
async def get_progress(user_id: str = Query(..., description="The user ID to query")):
    conn = await db._connect()
    cursor = await conn.cursor()
    await cursor.execute(
        'SELECT task_details, status, details, timestamp FROM tasks WHERE user_id = ? ORDER BY timestamp DESC LIMIT 1',
        (user_id,))
    record = await cursor.fetchone()
    await conn.close()

    if not record:
        raise HTTPException(status_code=404, detail="No progress found for the user.")

    progress = {"task_details": record[0], "status": record[1], "details": record[2], "timestamp": record[3]}
    return {"user_id": user_id, "progress": progress}


@app.get("/progress")
async def get_progress():
    progress = context_cache.get("progress", {})
    current_user = context_cache.get("current_user")
    current_progress = {"progress": progress, "current_user": current_user}
    logger.debug(f"Current progress: {current_progress}")
    return current_progress


@app.get("/history")
async def get_user_history(user_id: str = Query(..., description="User ID to query")):
    conn = await db._connect()
    cursor = await conn.cursor()
    await cursor.execute('SELECT task_details, completion_status, status, details, timestamp FROM tasks WHERE user_id = ? ORDER BY timestamp DESC', (user_id,))
    records = await cursor.fetchall()
    await conn.close()

    if not records:
        raise HTTPException(status_code=404, detail="No history found for the user.")

    history = [{"task_details": record[0], "completion_status": record[1], "status": record[2], "details": record[3], "timestamp": record[4]} for record in records]
    return {"user_id": user_id, "history": history}
