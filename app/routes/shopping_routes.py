"""
Маршруты для работы со списком покупок
"""
from flask import Blueprint, request, jsonify, render_template
from app.services.shopping_service import ShoppingService
from app.utils.logger import setup_logger

logger = setup_logger(__name__)
shopping_routes = Blueprint('shopping_routes', __name__)
shopping_service = ShoppingService()

@shopping_routes.route('/shopping_list')
def shopping_list():
    """
    Отображает страницу списка покупок
    
    Returns:
        str: HTML страница списка покупок
    """
    logger.info("Запрос страницы списка покупок")
    return render_template('shopping_list.html')

@shopping_routes.route('/generate_shopping_list', methods=['POST'])
def generate_shopping_list():
    """
    Генерирует консолидированный список покупок из нескольких рецептов
    
    Ожидает JSON:
        - meals: список рецептов с их ингредиентами
    
    Returns:
        dict: JSON ответ с консолидированным списком покупок
    """
    try:
        data = request.get_json()
        meals = data.get('meals', [])
        
        logger.info(f"Запрос на генерацию списка покупок для {len(meals)} рецептов")
        
        shopping_list = shopping_service.generate_shopping_list(meals)
        
        return jsonify({"shopping_list": shopping_list})
        
    except Exception as e:
        logger.error(f"Ошибка при генерации списка покупок: {e}")
        return jsonify({
            "error": "Произошла ошибка при генерации списка покупок"
        }), 500
