"""Pemilihan makanan berdasarkan target makromolekul."""

from __future__ import annotations

import csv
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


MACRO_KEYS = ("carbs", "protein", "fat")


@dataclass(frozen=True)
class Food:
    name: str
    category: str
    carbs: float
    protein: float
    fat: float
    calories: float

    def macro_dict(self) -> dict[str, float]:
        return {
            "carbs": self.carbs,
            "protein": self.protein,
            "fat": self.fat,
            "calories": self.calories,
        }


@dataclass(frozen=True)
class MenuItem:
    food: Food
    servings: int

    @property
    def total_carbs(self) -> float:
        return self.food.carbs * self.servings

    @property
    def total_protein(self) -> float:
        return self.food.protein * self.servings

    @property
    def total_fat(self) -> float:
        return self.food.fat * self.servings

    @property
    def total_calories(self) -> float:
        return self.food.calories * self.servings


def load_foods(csv_path: str | Path) -> list[Food]:
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset makanan tidak ditemukan: {path}")

    foods: list[Food] = []
    with path.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        required_columns = {"name", "category", "carbs_g", "protein_g", "fat_g", "calories_kcal"}
        missing_columns = required_columns.difference(reader.fieldnames or [])
        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValueError(f"Kolom CSV belum lengkap: {missing}")

        for row_number, row in enumerate(reader, start=2):
            try:
                foods.append(
                    Food(
                        name=row["name"].strip(),
                        category=row["category"].strip(),
                        carbs=float(row["carbs_g"]),
                        protein=float(row["protein_g"]),
                        fat=float(row["fat_g"]),
                        calories=float(row["calories_kcal"]),
                    )
                )
            except (KeyError, ValueError) as exc:
                raise ValueError(f"Data makanan pada baris {row_number} tidak valid.") from exc

    if not foods:
        raise ValueError("Dataset makanan kosong.")
    return foods


def total_nutrition(menu_items: list[MenuItem]) -> dict[str, float]:
    return {
        "carbs": sum(item.total_carbs for item in menu_items),
        "protein": sum(item.total_protein for item in menu_items),
        "fat": sum(item.total_fat for item in menu_items),
        "calories": sum(item.total_calories for item in menu_items),
    }


def recommend_menu(
    foods: list[Food],
    target_macros: dict[str, float],
    target_calories: float,
    max_servings: int = 18,
    max_same_food: int = 3,
) -> list[MenuItem]:
    """Susun menu harian dengan greedy search yang mudah dijelaskan di laporan."""
    if target_calories <= 0:
        raise ValueError("Target kalori harus lebih dari 0.")
    if max_servings <= 0:
        raise ValueError("Jumlah porsi maksimum harus lebih dari 0.")

    selected_foods: list[Food] = []
    selected_counts: Counter[str] = Counter()
    current_totals = {"carbs": 0.0, "protein": 0.0, "fat": 0.0, "calories": 0.0}
    current_score = _menu_error(current_totals, target_macros, target_calories)

    while len(selected_foods) < max_servings and current_totals["calories"] < target_calories * 0.95:
        best_food: Food | None = None
        best_totals: dict[str, float] | None = None
        best_score = float("inf")

        for food in foods:
            if selected_counts[food.name] >= max_same_food:
                continue

            candidate_totals = _add_food_to_totals(current_totals, food)
            candidate_score = _menu_error(candidate_totals, target_macros, target_calories)

            if candidate_score < best_score:
                best_food = food
                best_totals = candidate_totals
                best_score = candidate_score

        if best_food is None or best_totals is None:
            break

        # Berhenti saat tambahan porsi membuat kualitas menu memburuk terlalu jauh.
        if best_score > current_score and current_totals["calories"] >= target_calories * 0.75:
            break

        selected_foods.append(best_food)
        selected_counts[best_food.name] += 1
        current_totals = best_totals
        current_score = best_score

    return _group_foods(selected_foods)


def rank_foods_by_goal(foods: list[Food], goal_key: str, limit: int = 5) -> list[Food]:
    if limit <= 0:
        return []

    scored_foods = sorted(foods, key=lambda food: _food_goal_score(food, goal_key))
    return scored_foods[:limit]


def _group_foods(foods: list[Food]) -> list[MenuItem]:
    food_by_name = {food.name: food for food in foods}
    counts: Counter[str] = Counter(food.name for food in foods)
    return [MenuItem(food=food_by_name[name], servings=count) for name, count in counts.items()]


def _add_food_to_totals(totals: dict[str, float], food: Food) -> dict[str, float]:
    return {
        "carbs": totals["carbs"] + food.carbs,
        "protein": totals["protein"] + food.protein,
        "fat": totals["fat"] + food.fat,
        "calories": totals["calories"] + food.calories,
    }


def _menu_error(totals: dict[str, float], target_macros: dict[str, float], target_calories: float) -> float:
    calorie_progress = min(totals["calories"] / max(target_calories, 1.0), 1.0)
    macro_error = sum(
        abs(totals[key] - (target_macros[key] * calorie_progress)) / max(target_macros[key], 1.0)
        for key in MACRO_KEYS
    ) / len(MACRO_KEYS)
    calorie_error = abs(totals["calories"] - target_calories) / max(target_calories, 1.0)

    macro_over_penalty = sum(
        max(0.0, totals[key] - target_macros[key]) / max(target_macros[key], 1.0)
        for key in MACRO_KEYS
    )
    calorie_over_penalty = max(0.0, totals["calories"] - target_calories * 1.05) / max(target_calories, 1.0)

    return (0.75 * macro_error) + (0.25 * calorie_error) + (0.5 * macro_over_penalty) + calorie_over_penalty


def _food_goal_score(food: Food, goal_key: str) -> float:
    calories = max(food.calories, 1.0)
    protein_density = food.protein / calories
    carbs_density = food.carbs / calories
    fat_density = food.fat / calories

    if goal_key == "weight_loss":
        return calories / 250 - protein_density * 8 + fat_density * 5
    if goal_key == "muscle_gain":
        return -protein_density * 7 - carbs_density * 4 - calories / 800
    return abs(0.45 - carbs_density * 4) + abs(0.25 - protein_density * 4) + abs(0.30 - fat_density * 9)
