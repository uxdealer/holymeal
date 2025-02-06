"""
Сервис для генерации промптов
"""
from typing import List, Optional
import random
from config.settings import get_config
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class PromptService:
    """Сервис для генерации промптов"""
    
    def __init__(self):
        self.config = get_config()
        # Списки для разнообразия блюд
        self.cooking_techniques = [
            "запекание в духовке",
            "приготовление на пару",
            "гриль",
            "тушение",
            "жарка на сковороде",
            "фритюр",
            "вок",
            "маринование",
        ]
        
        self.world_cuisines = [
            "итальянская",
            "японская",
            "китайская",
            "тайская",
            "индийская",
            "мексиканская",
            "средиземноморская",
            "французская",
            "корейская",
            "вьетнамская",
            "греческая",
            "испанская",
            "марокканская",
            "ливанская"
        ]
    
    def generate_meal_plan_prompt(
        self,
        people_count: int = None,
        meal_type: Optional[str] = None,
        excluded_ingredients: Optional[List[str]] = None,
        available_ingredients: Optional[List[str]] = None
    ) -> str:
        """
        Генерирует промпт для создания плана питания
        
        Args:
            people_count: Количество порций (если не указано, берется из конфигурации)
            meal_type: Тип приема пищи (завтрак/обед/ужин)
            excluded_ingredients: Исключаемые ингредиенты
            available_ingredients: Доступные ингредиенты
            
        Returns:
            str: Сгенерированный промпт
        """
        logger.debug(f"Генерация промпта для плана питания, {meal_type}, 1 порция")
        
        # Формируем контекст для типа блюда
        meal_context = self._get_meal_type_context(meal_type)
        
        # Формируем ограничения по ингредиентам
        excluded_str = self._format_excluded_ingredients(excluded_ingredients)
        available_str = self._format_available_ingredients(available_ingredients)
        
        # Формируем промпт для плана питания
        prompt = f"""Ты опытный шеф-повар. Предложи рецепт блюда на 1 порцию.{meal_context}{excluded_str}{available_str}
        
        Структура меню:
        - Пн-Чт:
            * 1 вариант завтрака
            * 1 вариант обеда
            * 1 вариант ужина
        - Пт-Вс:
            * 1 вариант завтрака
            * 1 вариант обеда
            * 1 вариант ужина
        
        ВАЖНО: 
        - Все блюда должны быть уникальными и не повторяться в течение недели!
        - Используй уникальные основные ингредиенты для каждого блюда
        - Избегай повторения основных ингредиентов между блюдами
        - Не обязательно использовать все предложенные доступные ингредиенты
        - Используй разные техники приготовления (варка, жарка, запекание, тушение, пароварка)
        - Учитывай сезонность продуктов
        - Предлагай разнообразные блюда разных кухонь мира
        
        Следуй этим диетическим рекомендациям:
        - Суточная норма калорий: {self.config.CALORIES_PER_DAY} ккал на человека
        - Соотношение макронутриентов: 
          * {self.config.PROTEIN_RATIO * 100}% белки (50% растительные, 50% животные)
          * {self.config.FAT_RATIO * 100}% жиры (60% растительные, 40% животные)
          * {self.config.CARB_RATIO * 100}% углеводы (преимущественно сложные)
        - 400г некрахмалистых овощей на человека в день
        - 200-300г ягод и фруктов на человека в день
        - Завтраки не должны быть сладкими
        
        {self._get_json_format_instructions()}"""
        
        logger.debug("Промпт для плана питания сгенерирован успешно")
        return prompt
        
    def generate_single_meal_prompt(
        self,
        people_count: int = None,
        meal_type: Optional[str] = None,
        excluded_ingredients: Optional[List[str]] = None,
        available_ingredients: Optional[List[str]] = None,
        required_ingredients: Optional[List[str]] = None
    ) -> str:
        """
        Генерирует промпт для создания отдельного блюда
        
        Args:
            people_count: Количество порций (если не указано, берется из конфигурации)
            meal_type: Тип приема пищи (завтрак/обед/ужин)
            excluded_ingredients: Исключаемые ингредиенты
            available_ingredients: Доступные ингредиенты
            required_ingredients: Обязательные ингредиенты
            
        Returns:
            str: Сгенерированный промпт
        """
        logger.debug(f"Генерация промпта для отдельного блюда, {meal_type}, 1 порция")
        
        # Выбираем случайную технику приготовления и кухню
        suggested_technique = random.choice(self.cooking_techniques)
        suggested_cuisine = random.choice(self.world_cuisines)
        
        # Формируем контекст для типа блюда
        meal_context = self._get_meal_type_context(meal_type)
        
        # Формируем ограничения по ингредиентам
        excluded_str = self._format_excluded_ingredients(excluded_ingredients)
        available_str = self._format_available_ingredients(available_ingredients)
        required_str = self._format_required_ingredients(required_ingredients)
        
        # Формируем промпт для отдельного блюда
        prompt = f"""Ты опытный шеф-повар. Предложи рецепт блюда на 1 порцию, используя кухню: {suggested_cuisine} и технику приготовления: {suggested_technique}.{meal_context}{excluded_str}{available_str}{required_str}
        
        КРИТИЧЕСКИ ВАЖНО: 
        - Создай АБСОЛЮТНО УНИКАЛЬНОЕ блюдо, которое не повторяет предыдущие рецепты
        - НЕ ИСПОЛЬЗУЙ основные ингредиенты, которые уже были в других блюдах
        - Сделай акцент на необычные сочетания вкусов и текстур:
          * Сочетай хрустящие и мягкие текстуры
          * Комбинируй кислые, соленые, острые и умами вкусы
          * Добавляй контрастные температуры (горячее + холодное)
        
        Используй следующие приемы для уникальности:
        - Замени привычные ингредиенты на экзотические аналоги
        - Добавь неожиданные, но сочетающиеся специи и приправы
        - Примени интересные техники нарезки и подачи
        - Используй сезонные и региональные продукты
        - Добавь элементы фьюжн-кухни
        
        Возможные техники приготовления:
        {', '.join(self.cooking_techniques)}
        
        Кухни мира для вдохновения:
        {', '.join(self.world_cuisines)}
        
        {self._get_json_format_instructions()}"""
        
        logger.debug("Промпт для отдельного блюда сгенерирован успешно")
        return prompt
        
    def _get_json_format_instructions(self) -> str:
        """Возвращает инструкции по формату JSON"""
        return """В списке ингредиентов указывай количество в расчете на ОДНУ порцию! Указывай точное количество в граммах для каждого ингредиента (например: "морковь - 100г", "лук - 150г"). Для жидкостей используй миллилитры (например: "молоко - 200мл"). Специи указывай в граммах (например: "соль - 5г").
        
        Ответ должен быть строго в формате JSON:
        {
            "name": "название блюда",
            "ingredients": ["ингредиент - количество", "например: морковь - 100г"],
            "instructions": ["пошаговые", "инструкции по приготовлению"],
            "cooking_time": "время приготовления в минутах",
            "calories_per_serving": "примерное количество калорий на порцию"
        }
        
        Используй только этот формат, без дополнительного текста."""
    
    def _get_meal_type_context(self, meal_type: Optional[str]) -> str:
        """Возвращает контекст для типа приема пищи"""
        if meal_type == "breakfast":
            return "\nЭто блюдо для ЗАВТРАКА. Предложи легкое, питательное блюдо, которое даст энергию на весь день. Завтраки не должны быть сладкими."
        elif meal_type == "lunch":
            return "\nЭто блюдо для ОБЕДА. Предложи сытное основное блюдо."
        elif meal_type == "dinner":
            return "\nЭто блюдо для УЖИНА. Предложи легкое, но питательное блюдо, которое легко переварится."
        return ""
    
    def _format_excluded_ingredients(self, ingredients: Optional[List[str]]) -> str:
        """Форматирует список исключаемых ингредиентов"""
        if not ingredients:
            return ""
        return f"\nНЕ ИСПОЛЬЗУЙ следующие ингредиенты: {', '.join(ingredients)}"
    
    def _format_available_ingredients(self, ingredients: Optional[List[str]]) -> str:
        """Форматирует список доступных ингредиентов"""
        if not ingredients:
            return ""
        # Выбираем случайно 30-50% доступных ингредиентов
        num_ingredients = max(1, random.randint(
            len(ingredients) // 3,
            len(ingredients) // 2
        ))
        selected = random.sample(ingredients, num_ingredients)
        return f"\nПостарайся использовать некоторые из следующих ингредиентов: {', '.join(selected)}"
    
    def _format_required_ingredients(self, ingredients: Optional[List[str]]) -> str:
        """Форматирует список обязательных ингредиентов"""
        if not ingredients:
            return ""
        return f"\nОБЯЗАТЕЛЬНО используй следующие ингредиенты: {', '.join(ingredients)}"
