from pathlib import Path
from ultralytics import YOLO

class YoloVideoTracker:
    def __init__(self):
        self.model = YOLO("yolo11n.pt")

    def run(self, input_path):
        results = self.model.track(input_path, save=True, device="cpu")
        output_path = str((Path(__file__).parent / results[0].save_dir / Path(results[0].path).name))
        return output_path

# 可选：本地测试
if __name__=="__main__":
    a=YoloVideoTracker()
    output=a.run("race_car.mp4")
    print(f"保存结果到{output}")
    output2=a.run("race_car.mp4") # run twice!
    print(f"保存结果到{output2}")
