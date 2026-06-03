from ultralytics import YOLO

model = YOLO("yolov8n.pt")

model.train(
    data="/Users/sandeepbisht/Documents/Sightlink Ai/Obstacle detection.yolov8/data.yaml",
    epochs=15,
    imgsz=416,
    batch=4,
    name="sightlink_model",
    device="cpu",
    workers=2,
    cache=False,
)

print("Training complete!")