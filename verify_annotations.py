import os
import json
from pathlib import Path
import logging
import cv2
import numpy as np

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Пути к данным
data_path = Path("data/SoccerNetGS/gamestate-2024")
dataset_path = Path("dataset")

# Категории
CATEGORIES = {
    0: "player",
    1: "goalkeeper",
    2: "referee",
    3: "ball"
}

def load_original_annotations(split, sequence_name):
    """Загрузка оригинальных аннотаций"""
    labels_path = data_path / split / sequence_name / "Labels-GameState.json"
    if not labels_path.exists():
        logging.error(f"Файл аннотаций не найден: {labels_path}")
        return None
    with open(labels_path, "r") as f:
        return json.load(f)

def verify_image_annotations(split, image_name, yolo_annotations, original_data):
    """Проверка соответствия аннотаций YOLO оригинальным данным"""
    try:
        # Получаем номер изображения из имени файла
        img_num = int(image_name.split('_')[1].split('.')[0])
        
        # Загружаем изображение для проверки размеров
        img_path = dataset_path / split / "images" / image_name
        if not img_path.exists():
            logging.error(f"Изображение не найдено: {img_path}")
            return False

        img = cv2.imread(str(img_path))
        if img is None:
            logging.error(f"Не удалось загрузить изображение: {img_path}")
            return False

        height, width = img.shape[:2]
        
        # Проверяем каждую аннотацию YOLO
        for yolo_ann in yolo_annotations:
            class_id, x_center, y_center, w, h = map(float, yolo_ann.strip().split())
            
            # Проверяем, что класс существует в оригинальных данных
            found = False
            for orig_ann in original_data["annotations"]:
                if orig_ann["category_id"] == int(class_id) + 1:  # +1 потому что в оригинале индексы с 1
                    # Проверяем координаты
                    orig_bbox = orig_ann["bbox_image"]
                    orig_x = orig_bbox["x_center"] / 1920
                    orig_y = orig_bbox["y_center"] / 1080
                    orig_w = orig_bbox["w"] / 1920
                    orig_h = orig_bbox["h"] / 1080
                    
                    # Допустимая погрешность
                    eps = 0.001
                    if (abs(orig_x - x_center) < eps and 
                        abs(orig_y - y_center) < eps and 
                        abs(orig_w - w) < eps and 
                        abs(orig_h - h) < eps):
                        found = True
                        break
            
            if not found:
                logging.error(f"Аннотация не найдена в оригинальных данных: {yolo_ann}")
                return False

        return True

    except Exception as e:
        logging.error(f"Ошибка при проверке изображения {image_name}: {str(e)}")
        return False

def verify_dataset():
    """Проверка всего датасета"""
    splits = ["train", "validation"]
    
    for split in splits:
        logging.info(f"Проверка {split}...")
        
        # Загружаем информацию о последовательностях
        sequences_info_path = data_path / f"{split}/sequences_info.json"
        with open(sequences_info_path, "r") as f:
            sequences_info = json.load(f)
        
        # Создаем словарь для быстрого поиска последовательностей
        sequence_map = {seq["name"]: seq for seq in sequences_info[split]}
        
        # Проверяем каждое изображение
        images_path = dataset_path / split / "images"
        labels_path = dataset_path / split / "labels"
        
        if not (images_path.exists() and labels_path.exists()):
            logging.error(f"Директории не найдены для {split}")
            continue
        
        total_images = 0
        valid_images = 0
        
        for img_file in images_path.glob("*.jpg"):
            total_images += 1
            label_file = labels_path / f"{img_file.stem}.txt"
            
            if not label_file.exists():
                logging.error(f"Файл аннотаций не найден: {label_file}")
                continue
            
            # Загружаем аннотации YOLO
            with open(label_file, "r") as f:
                yolo_annotations = f.readlines()
            
            # Получаем оригинальные аннотации
            # Имя файла в формате: split_XXXXXX.jpg
            # Нам нужно найти соответствующую последовательность
            img_num = int(img_file.stem.split('_')[1])
            
            # Ищем последовательность, к которой относится это изображение
            sequence_name = None
            for seq_name, seq_info in sequence_map.items():
                if seq_info["start_frame"] <= img_num <= seq_info["end_frame"]:
                    sequence_name = seq_name
                    break
            
            if sequence_name is None:
                logging.error(f"Не удалось найти последовательность для изображения {img_file.name}")
                continue
            
            original_data = load_original_annotations(split, sequence_name)
            if original_data is None:
                continue
            
            if verify_image_annotations(split, img_file.name, yolo_annotations, original_data):
                valid_images += 1
                logging.info(f"Изображение валидно: {img_file.name} (последовательность: {sequence_name})")
            else:
                logging.error(f"Изображение невалидно: {img_file.name} (последовательность: {sequence_name})")
        
        logging.info(f"Проверка {split} завершена. Всего изображений: {total_images}, валидных: {valid_images}")

if __name__ == "__main__":
    verify_dataset() 