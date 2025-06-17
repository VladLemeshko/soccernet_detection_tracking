import os
import json
import shutil
import random
import logging
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Пути к данным
data_path = Path("data/SoccerNetGS/gamestate-2024")
dataset_path = Path("dataset")

# Предопределенные категории и их маппинг на YOLO-индексы
CATEGORIES = {
    1: 0,  # player -> 0
    2: 1,  # goalkeeper -> 1
    3: 2,  # referee -> 2
    4: 3   # ball -> 3
}

def setup_directories():
    """Создание необходимой структуры директорий"""
    directories = [
        dataset_path / "train/images",
        dataset_path / "train/labels",
        dataset_path / "validation/images",
        dataset_path / "validation/labels"
    ]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        logging.info(f"Создана директория: {directory}")

def process_data(split, sample_percentage):
    """Обработка данных для train или validation"""
    try:
        sequences_info_path = data_path / f"{split}/sequences_info.json"
        if not sequences_info_path.exists():
            raise FileNotFoundError(f"Файл не найден: {sequences_info_path}")

        with open(sequences_info_path, "r") as f:
            sequences_info = json.load(f)

        all_images = []
        processed_sequences = 0

        for sequence in sequences_info[split]:
            sequence_name = sequence["name"]
            img_folder_path = data_path / split / sequence_name / "img1"
            labels_path = data_path / split / sequence_name / "Labels-GameState.json"

            if not (img_folder_path.exists() and labels_path.exists()):
                logging.warning(f"Пропуск последовательности {sequence_name}: отсутствуют необходимые файлы")
                continue

            with open(labels_path, "r") as f:
                labels_data = json.load(f)

            for img_info in labels_data["images"]:
                img_id = img_info["image_id"]
                img_filename = img_info["file_name"]
                img_full_path = img_folder_path / img_filename

                if not img_full_path.exists():
                    logging.warning(f"Изображение не найдено: {img_full_path}")
                    continue

                annotations = []
                for annotation in labels_data["annotations"]:
                    if annotation["image_id"] == img_id and annotation["category_id"] in CATEGORIES:
                        bbox = annotation["bbox_image"]
                        # Нормализуем координаты в диапазоне от 0 до 1
                        normalized_x_center = bbox["x_center"] / 1920
                        normalized_y_center = bbox["y_center"] / 1080
                        normalized_width = bbox["w"] / 1920
                        normalized_height = bbox["h"] / 1080

                        # Получаем YOLO-индекс для категории
                        yolo_class_id = CATEGORIES[annotation["category_id"]]
                        
                        # Сохраняем аннотации
                        annotations.append(
                            f"{yolo_class_id} {normalized_x_center:.6f} {normalized_y_center:.6f} "
                            f"{normalized_width:.6f} {normalized_height:.6f}\n"
                        )

                if annotations:  # Добавляем изображение только если есть аннотации
                    all_images.append((img_full_path, annotations))

            processed_sequences += 1
            if processed_sequences % 10 == 0:
                logging.info(f"Обработано {processed_sequences} последовательностей")

        if not all_images:
            raise ValueError(f"Нет доступных изображений для {split}")

        random.shuffle(all_images)
        sample_size = max(1, int(len(all_images) * sample_percentage))
        sampled_images = all_images[:sample_size]

        for image_counter, (img_full_path, annotations) in enumerate(sampled_images):
            new_img_filename = f"{split}_{image_counter:06d}.jpg"
            dst_img_path = dataset_path / f"{split}/images" / new_img_filename
            
            # Копируем изображение
            shutil.copy2(str(img_full_path), str(dst_img_path))
            
            # Создаем файл с аннотациями
            txt_file_path = dataset_path / f"{split}/labels" / f"{split}_{image_counter:06d}.txt"
            with open(txt_file_path, "w") as txt_file:
                txt_file.writelines(annotations)

            if (image_counter + 1) % 100 == 0:
                logging.info(f"Обработано {image_counter + 1} изображений для {split}")

        logging.info(f"Завершена обработка {split} с {len(sampled_images)} изображениями")

    except Exception as e:
        logging.error(f"Ошибка при обработке {split}: {str(e)}")
        raise

def main():
    """Основная функция"""
    try:
        setup_directories()
        
        # Сохранение имен классов
        yolo_names = ["player", "goalkeeper", "referee", "ball"]
        with open(dataset_path / "yolo_names.json", "w") as f:
            json.dump(yolo_names, f, indent=2)

        # Обработка данных
        process_data("train", 0.5)
        process_data("validation", 0.25)

        logging.info("Датасет успешно сформирован")

    except Exception as e:
        logging.error(f"Критическая ошибка: {str(e)}")
        raise

if __name__ == "__main__":
    main()

