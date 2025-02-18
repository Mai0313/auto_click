# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "ultralytics",
# ]
# ///
from ultralytics import YOLO
from ultralytics.engine.results import Results


def detect_objects(image_path: str) -> list[Results]:
    model = YOLO("./data/yolo11n.pt")
    results: list[Results] = model(image_path)
    return results


if __name__ == "__main__":
    image_path = "./logs/color/start.png"
    results = detect_objects(image_path)
    for result in results:
        boxes = result.boxes
        masks = result.masks
        keypoints = result.keypoints
        probs = result.probs
        obb = result.obb
        result.show()
