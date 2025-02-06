"""
Маршруты для работы с рецептами
"""
from typing import Dict, Any
from flask import Blueprint, request, jsonify
from app.services.meal_service import MealService
from app.utils.logger import setup_logger

logger = setup_logger(__name__)
meal_routes = Blueprint('meal_routes', __name__)
meal_service = MealService()

@meal_routes.route('/generate', methods=['POST'])
def generate():
    """
    Генерирует полный план питания с 6 уникальными рецептами
    
    Ожидает JSON:
        - peopleCount: количество порций
        - availableIngredients: список доступных ингредиентов
    
    Returns:
        dict: JSON ответ с планом питания
    """
    try:
        data = request.get_json()
        people_count = int(data.get('peopleCount', 2))
        available_ingredients = data.get('availableIngredients', [])
        
        logger.info(f"Запрос на генерацию плана питания на {people_count} человек")
        
        meals = meal_service.generate_meal_plan(
            people_count=people_count,
            available_ingredients=available_ingredients
        )
        
        return jsonify({"meal_plan": meals})
        
    except Exception as e:
        logger.error(f"Ошибка при генерации плана питания: {e}")
        return jsonify({
            "error": "Произошла ошибка при генерации плана питания"
        }), 500

@meal_routes.route('/regenerate_meal', methods=['POST'])
def regenerate_meal():
    """
    Регенерирует отдельный рецепт с учетом ограничений
    
    Ожидает JSON:
        - peopleCount: количество порций
        - excludedIngredients: исключаемые ингредиенты
        - availableIngredients: доступные ингредиенты
        - requiredIngredients: обязательные ингредиенты
        - mealIndex: индекс регенерируемого блюда
        - mealType: тип приема пищи
    
    Returns:
        dict: JSON ответ с новым рецептом
    """
    try:
        data = request.get_json()
        people_count = int(data.get('peopleCount', 2))
        excluded_ingredients = data.get('excludedIngredients', [])
        available_ingredients = data.get('availableIngredients', [])
        required_ingredients = data.get('requiredIngredients', [])
        meal_index = str(data.get('mealIndex', '0'))
        meal_type = data.get('mealType', 'lunch')
        
        logger.info(f"Запрос на регенерацию рецепта {meal_index} типа {meal_type}")
        
        meal = meal_service.regenerate_meal(
            people_count=people_count,
            meal_index=meal_index,
            meal_type=meal_type,
            excluded_ingredients=excluded_ingredients,
            available_ingredients=available_ingredients,
            required_ingredients=required_ingredients
        )
        
        return jsonify({"meal": meal})
        
    except Exception as e:
        logger.error(f"Ошибка при регенерации рецепта: {e}")
        return jsonify({
            "error": "Произошла ошибка при регенерации рецепта"
        }), 500

@meal_routes.route('/update_meal', methods=['POST'])
def update_meal():
    """
    Обновляет существующий рецепт с новыми ингредиентами
    
    Ожидает JSON:
        - peopleCount: количество порций
        - excludedIngredients: исключаемые ингредиенты
        - availableIngredients: доступные ингредиенты
        - ingredients: новый список обязательных ингредиентов
        - mealType: тип приема пищи
    
    Returns:
        dict: JSON ответ с обновленным рецептом
    """
    try:
        data = request.get_json()
        people_count = int(data.get('peopleCount', 2))
        excluded_ingredients = data.get('excludedIngredients', [])
        available_ingredients = data.get('availableIngredients', [])
        required_ingredients = data.get('ingredients', [])
        meal_type = data.get('mealType', 'lunch')
        
        logger.info(f"Запрос на обновление рецепта типа {meal_type}")
        
        meal = meal_service.regenerate_meal(
            people_count=people_count,
            meal_index='update',
            meal_type=meal_type,
            excluded_ingredients=excluded_ingredients,
            available_ingredients=available_ingredients,
            required_ingredients=required_ingredients
        )
        
        return jsonify({"meal": meal})
        
    except Exception as e:
        logger.error(f"Ошибка при обновлении рецепта: {e}")
        return jsonify({
            "error": "Произошла ошибка при обновлении рецепта"
        }), 500
