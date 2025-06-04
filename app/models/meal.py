"""
Модели данных для работы с рецептами
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Ingredient:
    """Модель ингредиента"""

    name: str
    amount: float
    unit: str

    def __str__(self) -> str:
        return f"{self.name} - {self.amount}{self.unit}"


@dataclass
class Meal:
    """Модель рецепта"""

    name: str
    ingredients: List[Ingredient]
    instructions: List[str]
    cooking_time: int
    calories_per_serving: int
    meal_type: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Meal":
        """
        Создает объект Meal из словаря

        Args:
            data (dict): Словарь с данными рецепта

        Returns:
            Meal: Объект рецепта
        """
        ingredients = []
        for ing_str in data.get("ingredients", []):
            name, amount_str = ing_str.split(" - ")
            # Извлекаем числовое значение и единицу измерения
            import re

            amount = float(re.findall(r"\d+", amount_str)[0])
            unit = "".join(re.findall(r"[а-яА-Я]+", amount_str))
            ingredients.append(Ingredient(name.strip(), amount, unit))

        return cls(
            name=data.get("name", ""),
            ingredients=ingredients,
            instructions=data.get("instructions", []),
            cooking_time=int(data.get("cooking_time", 0)),
            calories_per_serving=int(data.get("calories_per_serving", 0)),
            meal_type=data.get("meal_type"),
        )

    def to_dict(self) -> dict:
        """
        Преобразует объект в словарь

        Returns:
            dict: Словарь с данными рецепта
        """
        return {
            "name": self.name,
            "ingredients": [str(ing) for ing in self.ingredients],
            "instructions": self.instructions,
            "cooking_time": self.cooking_time,
            "calories_per_serving": self.calories_per_serving,
            "meal_type": self.meal_type,
        }

    def get_main_ingredients(self) -> List[str]:
        """
        Возвращает список основных ингредиентов (исключая специи и мелкие добавки)

        Returns:
            List[str]: Список основных ингредиентов
        """
        skip_ingredients = []

        main_ingredients = []
        for ing in self.ingredients:
            if (
                not any(skip in ing.name.lower() for skip in skip_ingredients)
                and ing.amount > 30
            ):
                main_ingredients.append(ing.name.lower())
        return main_ingredients
