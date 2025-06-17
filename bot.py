import telebot
import os
from datetime import datetime
from ultralytics import YOLO

curr_path = os.path.abspath(os.getcwd())

# Создаем папку для сохранения видео, если её нет
VIDEOS_DIR = "videos"
if not os.path.exists(VIDEOS_DIR):
    os.makedirs(VIDEOS_DIR)

VIDEOS_PROCESSED_DIR = "videos_processed"
if not os.path.exists(VIDEOS_PROCESSED_DIR):
    os.makedirs(VIDEOS_PROCESSED_DIR)

# Загрузка добученной модели
# путь к дообученной модели
model = YOLO(f"{curr_path}/runs/detect/train/weights/best.pt") 

def process_image(image_path):
    """Обработать изображение и показать результат"""
    # Запуск детекции
    results = model(image_path)
    
    # Визуализация результатов
    result_image = results[0].plot()
    
    # Показать изображение
    import cv2
    cv2.imshow("Detection Result", result_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    return results

def process_video(video_path, filename):
    """Обработать видео и сохранить результат"""
    results = model(video_path, stream=True)
    
    model.predict(video_path, save=True, project=VIDEOS_PROCESSED_DIR, name=filename)

BOT_TOKEN = '8143085793:AAGYLfrHJxcai9aj9KHepPBDRq62rIFxTNc'
bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я бот созданный для демонстрации проекта по компьютерному зрению, созданного Владиславом Лемешко и Дарой Чубаровой. Отправь мне видео футбольного матча, а я найду на нем игроков, реффери и даже мяч!")

# Функция для принятия и сохранения видео от пользователя
@bot.message_handler(content_types=['video'])
def handle_video(message):
    try:
        # Отправляем уведомление о получении видео
        bot.reply_to(message, "Получил видео! Начинаю обработку...")
        
        # Получаем информацию о файле
        file_info = bot.get_file(message.video.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # Создаем уникальное имя файла с временной меткой
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        user_id = message.from_user.id
        file_extension = file_info.file_path.split('.')[-1]
        filename_without_ext = f'video_{user_id}_{timestamp}'
        filename = f"{filename_without_ext}.{file_extension}"
        filepath = os.path.join(VIDEOS_DIR, filename)
        
        # Сохраняем файл на сервер
        with open(filepath, 'wb') as new_file:
            new_file.write(downloaded_file)
        bot.reply_to(message, f"Видео успешно сохранено как {filename}! Обработка началась.")
        
        # Здесь можно добавить вызов функции обработки видео
        #processed_video_path = process_video(filepath)  # твоя функция обработки
        processed_video_path = os.path.join(VIDEOS_PROCESSED_DIR, filename_without_ext, f'{filename_without_ext}.avi')
        process_video(filepath, filename_without_ext)
        #processed_video_path = filepath
        
        # После обработки отправляем видео обратно пользователю
        send_video_to_user(message.chat.id, processed_video_path)
        
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка при обработке видео: {str(e)}")

# Функция для отправки видео пользователю
def send_video_to_user(chat_id, video_path, caption="Обработанное видео"):
    try:
        # Проверяем, существует ли файл
        if not os.path.exists(video_path):
            bot.send_message(chat_id, "Ошибка: видео файл не найден!")
            return
        
        # Отправляем видео
        with open(video_path, 'rb') as video:
            bot.send_video(chat_id, video, caption=caption)
            
        print(f"Видео {video_path} успешно отправлено пользователю {chat_id}")
        
    except Exception as e:
        bot.send_message(chat_id, f"Ошибка при отправке видео: {str(e)}")
        print(f"Ошибка отправки видео: {str(e)}")

# Дополнительная команда для тестирования отправки существующего видео
@bot.message_handler(commands=['test_send'])
def test_send_video(message):
    # Пример использования функции отправки
    video_path = "path/to/your/video.mp4"  # укажи путь к тестовому видео
    send_video_to_user(message.chat.id, video_path, "Тестовое видео")

bot.infinity_polling()
