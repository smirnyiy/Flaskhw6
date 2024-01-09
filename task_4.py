from contextlib import asynccontextmanager
import databases
from fastapi import FastAPI
from sqlalchemy import create_engine, select, insert, update, delete

from .models_4 import TaskIn, TaskOut, Base, Task


DATABASE_URL = 'sqlite:///task_4.sqlite'

db = databases.Database(DATABASE_URL)
engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False})

Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.connect()

    yield

    await db.disconnect()


app = FastAPI(lifespan=lifespan, title='Задание 4', version='1.0')


# Function that returns a list of tasks
@app.get('/tasks/', response_model=list[TaskOut])
async def index():
    tasks = select(Task)

    return await db.fetch_all(tasks)


# Functions for edit the whole task information
@app.get('/tasks/{task_id}/', response_model=TaskOut)
async def get_task(task_id: int):
    task = await db.fetch_one(select(Task).where(Task.id == task_id))

    return task


@app.post('/tasks/', response_model=TaskIn)
async def create_task(task: TaskIn):
    new_task = insert(Task).values(**task.model_dump())
    await db.execute(new_task)

    return task


@app.put('/tasks/{task_id}/', response_model=TaskOut)
async def update_task(task_id: int, task: TaskIn):
    task_update = (
        update(Task).where(Task.id == task_id).values(**task.model_dump())
    )
    await db.execute(task_update)

    return await db.fetch_one(select(Task).where(Task.id == task_id))


@app.delete('/tasks/{task_id}/')
async def delete_task(task_id: int):
    sql_task = await db.fetch_one(select(Task).where(Task.id == task_id))
    task = TaskOut.model_validate(
        {
            'id': sql_task.id,
            'title': sql_task.title,
            'description': sql_task.description,
            'done': sql_task.done
        }
    )

    task_delete = delete(Task).where(Task.id == task_id)
    await db.execute(task_delete)

    return {'deleted': True, 'task': task.model_dump()}