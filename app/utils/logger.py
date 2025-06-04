"""
Модуль настройки логирования
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from config.settings import get_config


def setup_logger(name):
    """
    Настраивает и возвращает логгер с заданным именем

    Args:
        name (str): Имя логгера

    Returns:
        logging.Logger: Настроенный логгер
    """
    config = get_config()

    # Создаем логгер
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, config.LOG_LEVEL))

    # Создаем форматтер
    formatter = logging.Formatter(config.LOG_FORMAT)

    # Создаем директорию для логов если её нет
    os.makedirs(os.path.dirname(config.LOG_FILE), exist_ok=True)

    # Добавляем обработчик для файла с ротацией
    file_handler = RotatingFileHandler(
        config.LOG_FILE,
        maxBytes=config.LOG_MAX_SIZE,
        backupCount=config.LOG_BACKUP_COUNT,
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # В режиме разработки добавляем вывод в консоль
    if config.DEBUG:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger
