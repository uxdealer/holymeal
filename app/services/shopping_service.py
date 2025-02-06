"""
Сервис для работы со списком покупок
"""
from typing import List, Dict, Any
from app.models.meal import Meal
from app.models.shopping_list import ShoppingList
from app.utils.validators import ShoppingListValidator
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class ShoppingService:
    """Сервис для работы со списком покупок"""
    
    def generate_shopping_list(self, meals_data: List[Dict[str, Any]]) -> List[str]:
        """
        Генерирует список покупок на основе рецептов
        
        Args:
            meals_data: Список рецептов
            
        Returns:
            List[str]: Отсортированный список покупок
        """
        logger.info("Генерация списка покупок")
        
        # Валидируем входные данные
        validation_result = ShoppingListValidator.validate_shopping_list_data({
            'meals': meals_data
        })
        if not validation_result.is_valid:
            logger.error(f"Ошибка валидации данных: {validation_result.get_errors()}")
            return []
        
        # Создаем объект списка покупок
        shopping_list = ShoppingList()
        
        # Группируем блюда по типам (будни/выходные)
        weekday_meals = meals_data[:3]  # Первые 3 блюда для будних дней (Пн-Чт)
        weekend_meals = meals_data[3:]  # Последние 3 блюда для выходных (Пт-Вс)
        
        try:
            # Обрабатываем блюда для будних дней (4 дня)
            logger.debug("Обработка блюд для будних дней")
            self._process_meals(weekday_meals, shopping_list, days_multiplier=4)
            
            # Обрабатываем блюда для выходных (3 дня)
            logger.debug("Обработка блюд для выходных")
            self._process_meals(weekend_meals, shopping_list, days_multiplier=3)
            
            # Получаем отсортированный список
            result = shopping_list.get_sorted_items()
            logger.info(f"Список покупок сгенерирован успешно: {len(result)} позиций")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка при генерации списка покупок: {e}")
            return []
    
    def _process_meals(
        self,
        meals_data: List[Dict[str, Any]],
        shopping_list: ShoppingList,
        days_multiplier: int = 1
    ):
        """
        Обрабатывает список блюд и добавляет ингредиенты в список покупок
        
        Args:
            meals_data: Список рецептов
            shopping_list: Объект списка покупок
            multiplier: Множитель количества (например, для нескольких дней)
        """
        for meal_data in meals_data:
            try:
                # Создаем объект рецепта
                meal = Meal.from_dict(meal_data)
                # Добавляем ингредиенты в список покупок
                shopping_list.add_meal(meal, days_multiplier)
                logger.debug(f"Обработан рецепт: {meal.name}")
            except Exception as e:
                logger.error(f"Ошибка при обработке рецепта: {e}")
                continue
