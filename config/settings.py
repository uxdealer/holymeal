"""
Конфигурационные настройки приложения
"""
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

class Config:
    """Базовый класс конфигурации"""
    # Основные настройки приложения
    APP_NAME = "MealGen"
    DEBUG = False
    TESTING = False
    
    # API ключи
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    
    # Настройки Claude
    CLAUDE_MODEL = "claude-3-5-sonnet-latest"
    CLAUDE_MAX_TOKENS_TO_SAMPLE = 1000
    CLAUDE_TEMPERATURE = 1
    
    # Настройки генерации меню
    DEFAULT_PEOPLE_COUNT = 2  # Количество порций по умолчанию
    WEEKDAY_DAYS = 4     # Количество будних дней (Пн-Чт)
    WEEKEND_DAYS = 3     # Количество выходных дней (Пт-Вс)
    CALORIES_PER_DAY = 2000
    PROTEIN_RATIO = 0.20  # 20% белки
    FAT_RATIO = 0.30     # 30% жиры
    CARB_RATIO = 0.50    # 50% углеводы
    
    # Настройки логирования
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'logs/mealgen.log'
    LOG_MAX_SIZE = 10 * 1024 * 1024  # 10 MB
    LOG_BACKUP_COUNT = 5

class DevelopmentConfig(Config):
    """Конфигурация для разработки"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """Конфигурация для продакшена"""
    LOG_LEVEL = 'WARNING'

class TestingConfig(Config):
    """Конфигурация для тестирования"""
    TESTING = True
    LOG_LEVEL = 'DEBUG'

# Словарь доступных конфигураций
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

# Получение текущей конфигурации
def get_config():
    """Возвращает текущую конфигурацию на основе переменной окружения"""
    env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])
