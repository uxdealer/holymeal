"""
Модели данных для работы со списком покупок
"""

from dataclasses import dataclass
from typing import List, Dict
from .meal import Meal, Ingredient
from config.settings import get_config


@dataclass
class ShoppingItem:
    """Модель элемента списка покупок"""

    name: str
    amount: float
    unit: str

    def __str__(self) -> str:
        return f"{self.name} - {int(round(self.amount))} {self.unit}"


class ShoppingList:
    """Модель списка покупок"""

    def __init__(self):
        self.items: Dict[str, ShoppingItem] = {}

    def add_meal(self, meal: Meal, days_multiplier: int = 1):
        """
        Добавляет ингредиенты из рецепта в список покупок

        Args:
            meal (Meal): Рецепт для добавления
            days_multiplier (int): Множитель дней (4 для будних, 3 для выходных)
        """
        # Получаем конфигурацию для доступа к DEFAULT_PEOPLE_COUNT
        config = get_config()

        # Умножаем на количество порций и дней
        total_multiplier = config.DEFAULT_PEOPLE_COUNT * days_multiplier

        for ingredient in meal.ingredients:
            self._add_ingredient(ingredient, total_multiplier)

    def _add_ingredient(self, ingredient: Ingredient, multiplier: int = 1):
        """
        Добавляет ингредиент в список покупок

        Args:
            ingredient (Ingredient): Ингредиент для добавления
            multiplier (int): Множитель количества
        """
        # Пропускаем специи и мелкие ингредиенты
        skip_ingredients = []

        if any(skip in ingredient.name.lower() for skip in skip_ingredients):
            return

        name = ingredient.name.lower()
        if name in self.items:
            # Если ингредиент уже есть в списке и единицы измерения совпадают
            if self.items[name].unit == ingredient.unit:
                self.items[name].amount += ingredient.amount * multiplier
        else:
            # Добавляем новый ингредиент
            self.items[name] = ShoppingItem(
                name=ingredient.name,
                amount=ingredient.amount * multiplier,
                unit=ingredient.unit,
            )

    def get_sorted_items(self) -> List[str]:
        """
        Возвращает отсортированный список покупок

        Returns:
            List[str]: Отсортированный список ингредиентов с количествами
        """
        return [str(item) for item in sorted(self.items.values(), key=lambda x: x.name)]

    def clear(self):
        """Очищает список покупок"""
        self.items.clear()
