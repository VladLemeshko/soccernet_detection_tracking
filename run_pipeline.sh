#!/bin/bash

# Создаем директорию для логов
mkdir -p logs

# Функция для логирования
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a logs/pipeline.log
}

# # Создаем и активируем виртуальное окружение
log "Создание виртуального окружения..."
python3 -m venv venv 2>&1 | tee -a logs/venv_setup.log
source venv/bin/activate

# Устанавливаем зависимости
log "Установка зависимостей..."
pip install ultralytics opencv-python SoccerNet 2>&1 | tee -a logs/dependencies.log

# Проверяем наличие GPU
if ! command -v nvidia-smi &> /dev/null; then
    log "GPU не найдена. Установка CPU версии PyTorch..."
    pip install torch torchvision torchaudio 2>&1 | tee -a logs/pytorch_install.log
else
    log "GPU найдена. Установка CUDA версии PyTorch..."
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 2>&1 | tee -a logs/pytorch_install.log
fi

# # Создаем необходимые директории
log "Создание директорий..."
mkdir -p data/SoccerNetGS
mkdir -p dataset

# Запускаем скрипты по порядку
log "1. Скачивание данных..."
python download_data.py 2>&1 | tee -a logs/download.log

log "2. Подготовка данных..."
python data_preparation.py 2>&1 | tee -a logs/preparation.log

log "3. Создание data.yaml..."
python data_yolo_preparting.py 2>&1 | tee -a logs/yolo_prep.log

log "4. Обработка challenge данных..."
python process_challenge_data.py 2>&1 | tee -a logs/challenge.log

log "5. Запуск обучения модели..."
python3 model_train.py 2>&1 | tee -a logs/training.log

log "6. Генерация тестового видео..."
python test_video_generating.py 2>&1 | tee -a logs/video_gen.log

log "Готово! Все этапы выполнены. Логи сохранены в директории logs/" 
