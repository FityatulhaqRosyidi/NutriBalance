"""Perhitungan kebutuhan kalori dan makromolekul."""

from __future__ import annotations

from dataclasses import dataclass


ACTIVITY_FACTORS = {
    "rendah": 1.2,
    "sedang": 1.55,
    "tinggi": 1.725,
}

GOAL_PROFILES = {
    "weight_loss": {
        "label": "Weight loss",
        "description": "Defisit kalori ringan untuk membantu penurunan berat badan.",
        "calorie_multiplier": 0.85,
        "ratios": {"carbs": 0.40, "protein": 0.35, "fat": 0.25},
    },
    "maintain": {
        "label": "Maintain weight",
        "description": "Kalori pemeliharaan untuk menjaga berat badan.",
        "calorie_multiplier": 1.00,
        "ratios": {"carbs": 0.45, "protein": 0.25, "fat": 0.30},
    },
    "muscle_gain": {
        "label": "Muscle gain",
        "description": "Surplus kalori ringan untuk mendukung pembentukan otot.",
        "calorie_multiplier": 1.10,
        "ratios": {"carbs": 0.50, "protein": 0.30, "fat": 0.20},
    },
}

MACRO_CALORIES_PER_GRAM = {
    "carbs": 4,
    "protein": 4,
    "fat": 9,
}


@dataclass(frozen=True)
class MacroTargets:
    carbs: float
    protein: float
    fat: float

    def as_dict(self) -> dict[str, float]:
        return {
            "carbs": self.carbs,
            "protein": self.protein,
            "fat": self.fat,
        }


@dataclass(frozen=True)
class NutritionPlan:
    bmr: float
    maintenance_calories: float
    daily_calories: float
    goal_key: str
    activity_key: str
    macro_ratios: dict[str, float]
    macro_targets: MacroTargets


def normalize_gender(raw_gender: str) -> str:
    value = raw_gender.strip().lower()
    male_values = {"1", "l", "lk", "laki-laki", "laki", "pria", "male", "m"}
    female_values = {"2", "p", "pr", "perempuan", "wanita", "female", "f"}

    if value in male_values:
        return "male"
    if value in female_values:
        return "female"
    raise ValueError("Jenis kelamin harus 1 untuk laki-laki atau 2 untuk perempuan.")


def normalize_activity(raw_activity: str) -> str:
    value = raw_activity.strip().lower()
    mapping = {
        "1": "rendah",
        "rendah": "rendah",
        "low": "rendah",
        "2": "sedang",
        "sedang": "sedang",
        "medium": "sedang",
        "3": "tinggi",
        "tinggi": "tinggi",
        "high": "tinggi",
    }

    if value in mapping:
        return mapping[value]
    raise ValueError("Aktivitas harus rendah, sedang, atau tinggi.")


def normalize_goal(raw_goal: str) -> str:
    value = raw_goal.strip().lower().replace(" ", "_").replace("-", "_")
    mapping = {
        "1": "weight_loss",
        "diet": "weight_loss",
        "weight_loss": "weight_loss",
        "loss": "weight_loss",
        "turun": "weight_loss",
        "2": "maintain",
        "maintain": "maintain",
        "maintain_weight": "maintain",
        "jaga": "maintain",
        "3": "muscle_gain",
        "muscle_gain": "muscle_gain",
        "bulking": "muscle_gain",
        "gain": "muscle_gain",
    }

    if value in mapping:
        return mapping[value]
    raise ValueError("Tujuan harus weight loss, maintain weight, atau muscle gain.")


def calculate_bmr(age: int, weight_kg: float, height_cm: float, gender: str) -> float:
    """Hitung BMR memakai rumus Mifflin-St Jeor."""
    if not 1 <= age <= 120:
        raise ValueError("Umur harus berada pada rentang 1 sampai 120 tahun.")
    if not 20 <= weight_kg <= 300:
        raise ValueError("Berat badan harus berada pada rentang 20 sampai 300 kg.")
    if not 80 <= height_cm <= 250:
        raise ValueError("Tinggi badan harus berada pada rentang 80 sampai 250 cm.")

    normalized_gender = normalize_gender(gender)
    base_bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age

    if normalized_gender == "male":
        return base_bmr + 5
    return base_bmr - 161


def calculate_macro_targets(daily_calories: float, goal_key: str) -> MacroTargets:
    if daily_calories <= 0:
        raise ValueError("Kalori harian harus lebih dari 0.")
    if goal_key not in GOAL_PROFILES:
        raise ValueError("Tujuan diet tidak dikenal.")

    ratios = GOAL_PROFILES[goal_key]["ratios"]
    return MacroTargets(
        carbs=(daily_calories * ratios["carbs"]) / MACRO_CALORIES_PER_GRAM["carbs"],
        protein=(daily_calories * ratios["protein"]) / MACRO_CALORIES_PER_GRAM["protein"],
        fat=(daily_calories * ratios["fat"]) / MACRO_CALORIES_PER_GRAM["fat"],
    )


def build_nutrition_plan(
    age: int,
    weight_kg: float,
    height_cm: float,
    gender: str,
    activity: str,
    goal: str,
) -> NutritionPlan:
    activity_key = normalize_activity(activity)
    goal_key = normalize_goal(goal)
    bmr = calculate_bmr(age, weight_kg, height_cm, gender)
    maintenance_calories = bmr * ACTIVITY_FACTORS[activity_key]
    daily_calories = maintenance_calories * GOAL_PROFILES[goal_key]["calorie_multiplier"]
    macro_targets = calculate_macro_targets(daily_calories, goal_key)

    return NutritionPlan(
        bmr=bmr,
        maintenance_calories=maintenance_calories,
        daily_calories=daily_calories,
        goal_key=goal_key,
        activity_key=activity_key,
        macro_ratios=GOAL_PROFILES[goal_key]["ratios"],
        macro_targets=macro_targets,
    )
