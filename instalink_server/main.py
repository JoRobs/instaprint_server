import subprocess
from uuid import uuid4
from anyio import create_task_group, sleep
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    out = subprocess.run(["bash", "-c", "instantlink"], capture_output=True)
    return {"message": out.stderr.decode("utf-8")}

@app.get("/dummy_task")
async def dummy_task_endpoint():
    task_id = uuid4()
    async with create_task_group() as tg:
        tg.start_soon(dummy_task, task_id)
    
    return {"message": f"Task {task_id} started"}

async def dummy_task(task_id: str):
    print(f"Task {task_id} running")
    await sleep(5)
    print(f"Task {task_id} finished")

