# я сделал задание А. Вот мой код
import os
import json
import time
import shutil
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ================= ФУНКЦИИ =================
def get_unique_name(folder_path, filename):
    """Проверяет, существует ли файл в папке, и если существует - создает уникальное имя."""

    name, ext = os.path.splitext(filename)
    counter = 1
    new_name = filename

    while os.path.exists(os.path.join(folder_path, new_name)):
        new_name = f"{name}_{counter}{ext}"
        counter += 1

    return new_name

def sort_file(file_path):
    """Сортирует один файл по правилам"""
    filename = os.path.basename(file_path)

    # Определение расширения
    if filename.startswith('.') and filename.count('.') == 1:
        extension = None
    elif '.' in filename:
        part = filename.split('.')[-1]
        extension = "." + part.lower()
    else:
        extension = None
    
    # Поиск папки
    target_folder = None
    for folder, extensions in rules.items():
        if extension in extensions:
            target_folder = folder
            break
    
    if target_folder:
        folder_path = os.path.join(my_downloads, target_folder)
        filename = os.path.basename(file_path)
        unique_name = get_unique_name(folder_path, filename)
        new_path = os.path.join(folder_path, unique_name)
        os.makedirs(folder_path, exist_ok=True)
        shutil.move(file_path, new_path)

        if filename == unique_name:
            logging.info(f'{filename} -> {target_folder}')
        else:
            logging.info(f'{filename} -> {target_folder} (переименован в {unique_name})')
    else:
        logging.warning(f"Неизвестный тип: {filename}")

# ================= НАСТРОЙКИ ЛОГИРОВАНИЯ =================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("organaizer.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# ================= ЗАГРУЗКА ПРАВИЛ =================
config_file = "config.json"
example_file = "config.example.json"

try:
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            rules = json.load(f)
        logging.info("Правила загружены из config.json")
    elif os.path.exists(example_file):
        logging.warning("Файл config.json не найден. Использую config.example.json")
        logging.warning("Создайте config.json для изменения правил")
        with open(example_file, 'r', encoding='utf-8') as f:
            rules = json.load(f)
except FileNotFoundError:
    logging.error("Файл config.json не найден!")
    logging.error("Создайте файл config.json с правилами сортировки!")
    exit()
except json.JSONDecodeError:
    logging.error("Ошибка в файле config.json - неправильный формат JSON!")
    exit()

# ================= КЛАСС-ОБРАБОТЧИК =================
class OrganizerHandler(FileSystemEventHandler):
    """Обработчик событий watchdog"""

    def on_created(self, event):
        """Когда файл создан или скачан"""
        if not event.is_directory:
            time.sleep(1.5)

            # Проверка, существует ли файл
            if not os.path.exists(event.src_path):
                logging.warning(f"Файл {os.path.basename(event.src_path)} не найден, пропускаем")
                return
            
            # Проверка, не является ли это временным файлом браузера
            filename = os.path.basename(event.src_path)
            if filename.endswith('.crdownload') or filename.endswith('.part'):
                logging.info(f"Пропускаем временный файл: {filename}")
                return

            logging.info(f"Обнаружен новый файл: {os.path.basename(event.src_path)}")
            sort_file(event.src_path)

# ================= ПУТЬ К ГЛОБАЛЬНОЙ ПАПКЕ =================
my_downloads = os.path.expanduser("~/Downloads")

# ================= ОСНОВНАЯ ЧАСТЬ =================
if __name__ == "__main__":
    # Сортировка существующих файлов
    logging.info("Начинаю сортировку существующих файлов...")
    for file in os.listdir(my_downloads):
        way = os.path.join(my_downloads, file)

        if os.path.isfile(way):
            sort_file(way)
    logging.info("Сортировка существующих файлов завершена")

    # Запуск наблюдателя
    time.sleep(1)
    logging.info("Запускаю режим наблюдателя...")
    event_handler = OrganizerHandler()
    observer = Observer()
    observer.schedule(event_handler, my_downloads, recursive=False)
    observer.start()

    logging.info(f"Слежу за папкой: {my_downloads}")
    logging.info("Нажми Ctrl+C для остановки")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logging.info("Программа остановлена")

    observer.join()