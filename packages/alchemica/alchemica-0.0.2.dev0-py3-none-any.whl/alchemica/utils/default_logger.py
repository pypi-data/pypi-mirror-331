import logging


def get_logger() -> logging.Logger:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)  # Устанавливаем уровень логирования
    console_handler = logging.StreamHandler()  # Создаем обработчик для вывода в консоль
    console_handler.setLevel(logging.INFO)  # Устанавливаем уровень для консольного вывода
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)  # Применяем форматирование
    logger.addHandler(console_handler)  # Добавляем обработчик к логгеру
    return logger


default_logger = get_logger()
