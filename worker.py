from celery import Celery
from algorithm.yolo_video import YoloVideoTracker
import os
from pathlib import Path
from contextlib import contextmanager
from config import output_dir

celery_app = Celery()
celery_app.config_from_object("config") # 从config.py读取配置

@contextmanager
def algorithm_cwd():
    prev_cwd = Path.cwd()
    os.chdir(Path(__file__).parent / "algorithm")
    try:
        yield
    finally:
        os.chdir(prev_cwd)

with algorithm_cwd():
    tracker = YoloVideoTracker()

@celery_app.task
def run_yolo_task(video_path: str):
    with algorithm_cwd():
        output_path = Path(tracker.run(video_path)).resolve()

    output_root = Path(output_dir).resolve()
    relative_path = output_path.relative_to(output_root)
    return f"/results/{relative_path.as_posix()}"
