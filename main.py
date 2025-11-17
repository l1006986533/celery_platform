import subprocess
import uvicorn
from fastapi import FastAPI, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from worker import run_yolo_task
import shutil
import time
from config import upload_dir, output_dir

app = FastAPI()

Path(upload_dir).mkdir(exist_ok=True)
Path(output_dir).mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/results", StaticFiles(directory=output_dir), name="results")

@app.get("/")
async def read_root():
    return FileResponse("static/index.html")

@app.post("/track")
async def track_video(file: UploadFile):
    input_path = (Path(upload_dir) / f"{time.time()}_{file.filename}").resolve()
    with open(input_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    task = run_yolo_task.delay(str(input_path))
    return {"task_id": task.id}

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    task = run_yolo_task.AsyncResult(task_id)
    if task.state == "PENDING":
        return {"status": task.state}
    elif task.state == "SUCCESS":
        output_path = task.result
        return {"status": task.state, "output": output_path}
    else:
        return {"status": task.state, "error": task.traceback}


if __name__ == "__main__":
    # Use Celery thread pool for concurrency without forking.
    proc = subprocess.Popen(["celery", "-A", "worker", "worker", "-P", "threads"])

    try:
        uvicorn.run("main:app", host="0.0.0.0", port=8000)
    finally:
        print(f"正在关闭worker[{proc.pid}]")
        if proc.poll() is None:
            proc.terminate()
        proc.wait()
