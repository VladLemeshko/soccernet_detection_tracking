from ultralytics import YOLO

model = YOLO("yolov8l.pt")

# Тренируем модель используя GPU
results = model.train(data="dataset/data.yaml", epochs=30, imgsz=1280, device='0')

