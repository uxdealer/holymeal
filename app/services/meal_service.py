"""
Сервис для работы с рецептами
"""
import json
from typing import List, Dict, Any, Optional
from anthropic import Anthropic
from config.settings import get_config
from app.models.meal import Meal
from app.services.prompt_service import PromptService
from app.utils.validators import MealValidator
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class MealService:
    """Сервис для работы с рецептами"""
    
    def __init__(self):
        self.config = get_config()
        self.anthropic = Anthropic(api_key=self.config.ANTHROPIC_API_KEY)
        self.prompt_service = PromptService()
        self.previous_meals: Dict[str, Meal] = {}  # последнее сгенерированное блюдо для каждого индекса
        self.meal_history: Dict[str, List[Meal]] = {}  # история блюд для каждого индекса
        self.session_history: List[Meal] = []  # общая история всех сгенерированных блюд за сессию
    
    def generate_meal_plan(
        self,
        people_count: int,
        available_ingredients: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Генерирует план питания
        
        Args:
            people_count: Количество порций
            available_ingredients: Список доступных ингредиентов
            
        Returns:
            List[Dict[str, Any]]: Список рецептов
        """
        logger.info(f"Генерация плана питания на {people_count} человек")
        
        meals = []
        used_ingredients = []
        meal_types = ['breakfast', 'lunch', 'dinner'] * 2  # Для будней и выходных
        
        for meal_type in meal_types:
            prompt = self.prompt_service.generate_meal_plan_prompt(
                people_count=people_count,
                meal_type=meal_type,
                excluded_ingredients=used_ingredients,
                available_ingredients=available_ingredients
            )
            
            # Пытаемся сгенерировать уникальное блюдо
            max_attempts = 2
            unique_meal_found = False
            last_valid_meal = None
            
            for attempt in range(max_attempts):
                logger.debug(f"Попытка генерации {attempt + 1}/{max_attempts}")
                
                meal_data = self._get_claude_response(prompt)
                
                # Валидируем полученные данные
                validation_result = MealValidator.validate_meal_data(meal_data)
                if not validation_result.is_valid:
                    logger.error(f"Ошибка валидации рецепта: {validation_result.get_errors()}")
                    continue
                
                # Создаем объект рецепта
                meal = Meal.from_dict(meal_data)
                meal.meal_type = meal_type
                
                # Сохраняем последний валидный рецепт
                last_valid_meal = meal
                
                # Проверяем уникальность относительно всей истории
                if self._is_unique_across_history(meal):
                    # Добавляем основные ингредиенты в список использованных
                    used_ingredients.extend(meal.get_main_ingredients())
                    
                    # Добавляем в общую историю сессии
                    self.session_history.append(meal)
                    
                    meals.append(meal.to_dict())
                    logger.debug(f"Сгенерирован уникальный рецепт: {meal.name}")
                    unique_meal_found = True
                    break
                else:
                    logger.debug(f"Блюдо {meal.name} похоже на существующее в истории")
                    # Генерируем новый промпт для следующей попытки
                    prompt = self.prompt_service.generate_meal_plan_prompt(
                        people_count=people_count,
                        meal_type=meal_type,
                        excluded_ingredients=used_ingredients,
                        available_ingredients=available_ingredients
                    )
            
            # Если не удалось найти уникальное блюдо, используем последнее валидное
            if not unique_meal_found and last_valid_meal:
                logger.warning(f"Не удалось сгенерировать уникальный рецепт, используем последний валидный: {last_valid_meal.name}")
                used_ingredients.extend(last_valid_meal.get_main_ingredients())
                self.session_history.append(last_valid_meal)
                meals.append(last_valid_meal.to_dict())
        
        logger.info("План питания сгенерирован успешно")
        return meals
    
    def regenerate_meal(
        self,
        people_count: int,
        meal_index: str,
        meal_type: str,
        excluded_ingredients: Optional[List[str]] = None,
        available_ingredients: Optional[List[str]] = None,
        required_ingredients: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Регенерирует отдельный рецепт
        
        Args:
            people_count: Количество порций
            meal_index: Индекс рецепта
            meal_type: Тип приема пищи
            excluded_ingredients: Исключаемые ингредиенты
            available_ingredients: Доступные ингредиенты
            required_ingredients: Обязательные ингредиенты
            
        Returns:
            Dict[str, Any]: Новый рецепт
        """
        logger.info(f"Регенерация рецепта {meal_index} типа {meal_type}")
        
        # Получаем предыдущий рецепт для сравнения
        previous_meal = self.previous_meals.get(meal_index)
        
        # Пытаемся сгенерировать достаточно отличающийся рецепт
        max_attempts = 5  # Увеличено количество попыток для отдельной регенерации
        unique_meal_found = False
        last_valid_meal = None
        
        for attempt in range(max_attempts):
            logger.debug(f"Попытка генерации {attempt + 1}/{max_attempts}")
            
            prompt = self.prompt_service.generate_single_meal_prompt(
                people_count=people_count,
                meal_type=meal_type,
                excluded_ingredients=excluded_ingredients,
                available_ingredients=available_ingredients,
                required_ingredients=required_ingredients
            )
            
            meal_data = self._get_claude_response(prompt)
            
            # Валидируем полученные данные
            validation_result = MealValidator.validate_meal_data(meal_data)
            if not validation_result.is_valid:
                logger.error(f"Ошибка валидации рецепта: {validation_result.get_errors()}")
                continue
            
            # Создаем объект рецепта
            meal = Meal.from_dict(meal_data)
            meal.meal_type = meal_type
            
            # Сохраняем последний валидный рецепт
            last_valid_meal = meal
            
            # Проверяем уникальность относительно всей истории
            if self._is_unique_across_history(meal):
                # Сохраняем в историю индекса
                if meal_index not in self.meal_history:
                    self.meal_history[meal_index] = []
                self.previous_meals[meal_index] = meal
                self.meal_history[meal_index].append(meal)
                
                # Добавляем в общую историю сессии
                self.session_history.append(meal)
                
                logger.info(f"Рецепт успешно регенерирован: {meal.name}")
                unique_meal_found = True
                return meal.to_dict()
            else:
                logger.debug(f"Блюдо {meal.name} похоже на существующее в истории")
        
        # Если не удалось найти уникальное блюдо, используем последнее валидное
        if not unique_meal_found and last_valid_meal:
            logger.warning(f"Не удалось сгенерировать уникальный рецепт, используем последний валидный: {last_valid_meal.name}")
            # Сохраняем в историю индекса
            if meal_index not in self.meal_history:
                self.meal_history[meal_index] = []
            self.previous_meals[meal_index] = last_valid_meal
            self.meal_history[meal_index].append(last_valid_meal)
            
            # Добавляем в общую историю сессии
            self.session_history.append(last_valid_meal)
            return last_valid_meal.to_dict()
            
        logger.error("Не удалось сгенерировать валидный рецепт")
        return {
            "name": "Ошибка генерации",
            "ingredients": ["Не удалось сгенерировать рецепт"],
            "instructions": ["Пожалуйста, попробуйте еще раз"],
            "cooking_time": "0",
            "calories_per_serving": "0"
        }
    
    def _is_meal_similar(self, meal1: Meal, meal2: Meal) -> bool:
        """
        Проверяет, похожи ли рецепты
        
        Args:
            meal1: Первый рецепт
            meal2: Второй рецепт
            
        Returns:
            bool: True если рецепты похожи
        """
        if not meal1 or not meal2:
            return False
            
        # Проверяем схожесть названий (без учета регистра)
        if meal1.name.lower() == meal2.name.lower():
            return True
            
        ingredients1 = set(meal1.get_main_ingredients())
        ingredients2 = set(meal2.get_main_ingredients())
        
        # Считаем рецепты похожими, если у них совпадает хотя бы один основной ингредиент
        common_ingredients = ingredients1.intersection(ingredients2)
        return len(common_ingredients) > 0
    
    def _is_unique_across_history(self, new_meal: Meal) -> bool:
        """
        Проверяет уникальность блюда относительно всей истории сессии
        
        Args:
            new_meal: Новое блюдо для проверки
                
        Returns:
            bool: True если блюдо уникально
        """
        for historical_meal in self.session_history:
            if self._is_meal_similar(new_meal, historical_meal):
                return False
        return True
    
    def _get_claude_response(self, prompt: str) -> Dict[str, Any]:
        """
        Отправляет запрос к Claude и получает ответ
        
        Args:
            prompt: Промпт для генерации
            
        Returns:
            Dict[str, Any]: Ответ в формате JSON
        """
        try:
            message = self.anthropic.messages.create(
                model=self.config.CLAUDE_MODEL,
                max_tokens=self.config.CLAUDE_MAX_TOKENS_TO_SAMPLE,
                temperature=self.config.CLAUDE_TEMPERATURE,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            return json.loads(message.content[0].text)
            
        except Exception as e:
            logger.error(f"Ошибка при запросе к Claude API: {e}")
            return {
                "name": "Ошибка генерации",
                "ingredients": ["Произошла ошибка при получении рецепта"],
                "instructions": ["Пожалуйста, попробуйте еще раз"],
                "cooking_time": "0",
                "calories_per_serving": "0"
            }
