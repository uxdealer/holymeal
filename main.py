"""
Основной файл приложения Flask
"""
from flask import Flask, render_template
from app.routes.meal_routes import meal_routes
from app.routes.shopping_routes import shopping_routes
from app.utils.logger import setup_logger
from config.settings import get_config

logger = setup_logger(__name__)

def create_app():
    """
    Создает и настраивает приложение Flask
    
    Returns:
        Flask: Настроенное приложение Flask
    """
    app = Flask(__name__)
    config = get_config()
    
    # Применяем конфигурацию
    app.config.from_object(config)
    
    # Регистрируем маршруты
    app.register_blueprint(meal_routes)
    app.register_blueprint(shopping_routes)
    
    # Главная страница
    @app.route('/')
    def index():
        """
        Отображает главную страницу приложения
        
        Returns:
            str: HTML главной страницы
        """
        return render_template('index.html')
    
    # Обработчик ошибок
    @app.errorhandler(404)
    def not_found_error(error):
        """Обработчик ошибки 404"""
        logger.warning(f"Страница не найдена: {error}")
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Обработчик ошибки 500"""
        logger.error(f"Внутренняя ошибка сервера: {error}")
        return render_template('errors/500.html'), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    config = get_config()
    
    logger.info(f"Запуск приложения {config.APP_NAME}")
    app.run(debug=config.DEBUG)
