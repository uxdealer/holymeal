"""
Модуль для валидации данных
"""

from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class ValidationError:
    """Класс для ошибок валидации"""

    field: str
    message: str


class ValidationResult:
    """Результат валидации"""

    def __init__(self):
        self.errors: List[ValidationError] = []

    def add_error(self, field: str, message: str):
        """Добавляет ошибку валидации"""
        self.errors.append(ValidationError(field, message))

    @property
    def is_valid(self) -> bool:
        """Проверяет, прошла ли валидация успешно"""
        return len(self.errors) == 0

    def get_errors(self) -> Dict[str, List[str]]:
        """Возвращает словарь с ошибками"""
        errors_dict: Dict[str, List[str]] = {}
        for error in self.errors:
            if error.field not in errors_dict:
                errors_dict[error.field] = []
            errors_dict[error.field].append(error.message)
        return errors_dict


class MealValidator:
    """Валидатор для рецептов"""

    @staticmethod
    def validate_meal_data(data: Dict[str, Any]) -> ValidationResult:
        """
        Проверяет данные рецепта

        Args:
            data: Словарь с данными рецепта

        Returns:
            ValidationResult: Результат валидации
        """
        result = ValidationResult()

        # Проверяем обязательные поля
        required_fields = [
            "name",
            "ingredients",
            "instructions",
            "cooking_time",
            "calories_per_serving",
        ]
        for field in required_fields:
            if field not in data:
                result.add_error(field, f"Поле '{field}' обязательно")

        # Проверяем название
        if "name" in data and not isinstance(data["name"], str):
            result.add_error("name", "Название должно быть строкой")
        elif "name" in data and len(data["name"].strip()) == 0:
            result.add_error("name", "Название не может быть пустым")

        # Проверяем ингредиенты
        if "ingredients" in data:
            if not isinstance(data["ingredients"], list):
                result.add_error("ingredients", "Ингредиенты должны быть списком")
            else:
                for i, ing in enumerate(data["ingredients"]):
                    if not isinstance(ing, str):
                        result.add_error(
                            "ingredients", f"Ингредиент {i + 1} должен быть строкой"
                        )
                    elif " - " not in ing:
                        result.add_error(
                            "ingredients",
                            f"Ингредиент {i + 1} должен быть в формате 'название - количество'",
                        )

        # Проверяем инструкции
        if "instructions" in data:
            if not isinstance(data["instructions"], list):
                result.add_error("instructions", "Инструкции должны быть списком")
            else:
                for i, step in enumerate(data["instructions"]):
                    if not isinstance(step, str):
                        result.add_error(
                            "instructions", f"Шаг {i + 1} должен быть строкой"
                        )
                    elif len(step.strip()) == 0:
                        result.add_error(
                            "instructions", f"Шаг {i + 1} не может быть пустым"
                        )

        # Проверяем время приготовления
        if "cooking_time" in data:
            try:
                cooking_time = int(data["cooking_time"])
                if cooking_time <= 0:
                    result.add_error(
                        "cooking_time",
                        "Время приготовления должно быть положительным числом",
                    )
            except (ValueError, TypeError):
                result.add_error(
                    "cooking_time", "Время приготовления должно быть целым числом"
                )

        # Проверяем калории
        if "calories_per_serving" in data:
            try:
                calories = int(data["calories_per_serving"])
                if calories <= 0:
                    result.add_error(
                        "calories_per_serving",
                        "Количество калорий должно быть положительным числом",
                    )
            except (ValueError, TypeError):
                result.add_error(
                    "calories_per_serving",
                    "Количество калорий должно быть целым числом",
                )

        return result


class ShoppingListValidator:
    """Валидатор для списка покупок"""

    @staticmethod
    def validate_shopping_list_data(data: Dict[str, Any]) -> ValidationResult:
        """
        Проверяет данные списка покупок

        Args:
            data: Словарь с данными списка покупок

        Returns:
            ValidationResult: Результат валидации
        """
        result = ValidationResult()

        # Проверяем наличие списка рецептов
        if "meals" not in data:
            result.add_error("meals", "Список рецептов обязателен")
            return result

        if not isinstance(data["meals"], list):
            result.add_error("meals", "Рецепты должны быть списком")
            return result

        # Проверяем каждый рецепт
        for i, meal in enumerate(data["meals"]):
            meal_result = MealValidator.validate_meal_data(meal)
            if not meal_result.is_valid:
                for error in meal_result.errors:
                    result.add_error(f"meals[{i}].{error.field}", error.message)

        return result
