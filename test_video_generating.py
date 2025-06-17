import os
import cv2

# Путь к папке с изображениями
image_folder = 'dataset/test/images'

# Имя выходного видео файла
video_name = 'test.mp4'

# Частота кадров
fps = 30

# Получаем список файлов в папке
images = [img for img in os.listdir(image_folder) if img.endswith(".jpg") or img.endswith(".png")]

# Сортируем файлы, чтобы они шли по порядку
images.sort()

# Проверяем, что изображения есть
if not images:
    print("Нет изображений для создания видео.")
else:
    # Считываем первое изображение, чтобы получить его размеры
    first_image_path = os.path.join(image_folder, images[0])
    first_frame = cv2.imread(first_image_path)
    height, width, layers = first_frame.shape

    # Создаем объект VideoWriter для записи видео
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Кодек для .mp4 файлов
    video = cv2.VideoWriter(video_name, fourcc, fps, (width, height))

    # Читаем и добавляем каждое изображение в видео
    for image in images:
        image_path = os.path.join(image_folder, image)
        frame = cv2.imread(image_path)
        video.write(frame)

    # Завершаем запись видео
    video.release()

    print(f"Видео {video_name} создано успешно!")

