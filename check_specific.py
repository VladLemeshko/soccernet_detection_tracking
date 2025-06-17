import json
from pathlib import Path
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Пути к данным
data_path = Path("/home/student/lemeshko/cv_project/data/SoccerNetGS/gamestate-2024")
dataset_path = Path("/home/student/lemeshko/cv_project/dataset")

def get_bbox_coordinates(ann):
    """Получение координат bbox из аннотации в разных форматах"""
    if "bbox_image" in ann:
        bbox = ann["bbox_image"]
        x_center = bbox["x_center"] / 1920
        y_center = bbox["y_center"] / 1080
        width = bbox["w"] / 1920
        height = bbox["h"] / 1080
    else:
        logging.error(f"Неизвестный формат bbox в аннотации: {ann}")
        return None
    
    return x_center, y_center, width, height

def check_specific_file():
    """Проверка конкретного файла аннотаций"""
    # Загружаем YOLO аннотации
    yolo_file = dataset_path / "train/labels/train_000000.txt"
    with open(yolo_file, "r") as f:
        yolo_annotations = f.readlines()
    
    # Загружаем оригинальные аннотации
    original_file = data_path / "train/SNGS-101/Labels-GameState.json"
    with open(original_file, "r") as f:
        original_data = json.load(f)
    
    # Находим соответствующие изображения в оригинальных данных
    target_image_id = "1101000265"
    for img_info in original_data["images"]:
        if img_info["image_id"] == target_image_id:
            logging.info(f"Найдено изображение: {img_info['file_name']}")
            
            # Получаем все аннотации для этого изображения
            img_annotations = []
            for ann in original_data["annotations"]:
                if ann["image_id"] == target_image_id:
                    bbox_coords = get_bbox_coordinates(ann)
                    if bbox_coords is None:
                        continue
                        
                    x_center, y_center, width, height = bbox_coords
                    
                    # Преобразуем категорию (в оригинале с 1, в YOLO с 0)
                    yolo_class = ann["category_id"] - 1
                    
                    img_annotations.append(f"{yolo_class} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")
            
            # Сортируем аннотации для сравнения
            yolo_annotations.sort()
            img_annotations.sort()
            
            # Выводим для сравнения
            logging.info("\nYOLO аннотации:")
            for ann in yolo_annotations:
                logging.info(ann.strip())
            
            logging.info("\nОригинальные аннотации:")
            for ann in img_annotations:
                logging.info(ann.strip())
            
            # Проверяем соответствие
            if len(yolo_annotations) != len(img_annotations):
                logging.error(f"Разное количество аннотаций: YOLO={len(yolo_annotations)}, Original={len(img_annotations)}")
                return
            
            # Сравниваем каждую аннотацию
            for yolo_ann, orig_ann in zip(yolo_annotations, img_annotations):
                if yolo_ann != orig_ann:
                    logging.error("Несоответствие в аннотациях:")
                    logging.error(f"YOLO: {yolo_ann.strip()}")
                    logging.error(f"Original: {orig_ann.strip()}")
                else:
                    logging.info(f"Аннотация совпадает: {yolo_ann.strip()}")
            
            return
    
    logging.error("Изображение не найдено в оригинальных данных")

if __name__ == "__main__":
    check_specific_file() 