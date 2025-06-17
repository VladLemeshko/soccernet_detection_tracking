import os
import json
import shutil

dataset_path = 'dataset'

# Функция для обработки тестовых данных (challenge)
os.makedirs(os.path.join(dataset_path, "test/images"), exist_ok=True)
def process_challenge_data():
    test_data_path = "data/SoccerNetGS/gamestate-2024/challenge/SNGS-007/img1"
    test_output_path = os.path.join(dataset_path, "test/images")

    # Создаем папку для сохранения тестовых изображений, если ее нет
    os.makedirs(test_output_path, exist_ok=True)

    # Проверяем, существует ли папка с изображениями
    if not os.path.exists(test_data_path):
        print(f"Папка с изображениями не существует: {test_data_path}")
        return

    # Получаем список файлов в папке с изображениями
    img_filenames = [f for f in os.listdir(test_data_path) if f.endswith(('.jpg', '.png', '.jpeg'))]

    if not img_filenames:
        print("Нет изображений в папке:", test_data_path)
        return

    # Сортируем файлы по числовым значениям
    img_filenames.sort(key=lambda x: int(os.path.splitext(x)[0]))  # Убираем расширение и сортируем по числу

    image_counter = 1  # Счетчик изображений

    for img_filename in img_filenames:
        img_full_path = os.path.join(test_data_path, img_filename)

        # Проверяем, существует ли файл
        if not os.path.exists(img_full_path):
            print("Image file does not exist:", img_full_path)
            continue

        # Генерируем новое имя файла
        new_img_filename = f"challenge_{image_counter:06d}.jpg"

        try:
            # Копируем изображение в выходную папку
            shutil.copy(img_full_path, os.path.join(test_output_path, new_img_filename))
        except Exception as e:
            print(f"Error copying {img_full_path} to {new_img_filename}: {e}")

        image_counter += 1

process_challenge_data()

