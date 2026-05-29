"""CLI Sistem Rekomendasi Diet Berdasarkan Komposisi Makromolekul."""

from __future__ import annotations

import argparse
from pathlib import Path

from nutribalance.nutrition_calculator import GOAL_PROFILES, build_nutrition_plan
from nutribalance.recommendation import (
    Food,
    MenuItem,
    load_foods,
    rank_foods_by_goal,
    recommend_menu,
    total_nutrition,
)
from nutribalance.visualization import (
    render_calorie_progress,
    render_macro_ratio_chart,
    render_target_vs_actual,
    save_png_charts,
)


DEFAULT_DATASET = Path(__file__).resolve().parents[2] / "data" / "makanan.csv"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sistem rekomendasi diet berdasarkan karbohidrat, protein, dan lemak."
    )
    parser.add_argument("--csv", default=str(DEFAULT_DATASET), help="Path dataset makanan CSV.")
    parser.add_argument("--no-png", action="store_true", help="Lewati penyimpanan grafik PNG opsional.")
    args = parser.parse_args()

    print("=" * 72)
    print("SISTEM REKOMENDASI DIET BERDASARKAN KOMPOSISI MAKROMOLEKUL")
    print("=" * 72)
    print("Program ini memakai BMR, faktor aktivitas, dan rasio makro untuk menyusun menu.\n")

    foods = load_foods(args.csv)
    plan = _collect_user_plan()
    target_macros = plan.macro_targets.as_dict()

    recommended_menu = recommend_menu(
        foods=foods,
        target_macros=target_macros,
        target_calories=plan.daily_calories,
        max_servings=_estimate_max_servings(plan.daily_calories),
    )
    actual_totals = total_nutrition(recommended_menu)

    _print_plan_summary(plan)
    _print_recommended_foods(foods, plan.goal_key)
    _print_menu(recommended_menu, actual_totals, plan.daily_calories)
    _print_visualizations(plan, actual_totals)

    if not args.no_png:
        success, message = save_png_charts(plan.macro_ratios, target_macros, actual_totals)
        print(f"\n{message}")
        if not success:
            print("Visualisasi ASCII tetap ditampilkan di terminal.")

    _run_food_log_if_requested(foods, target_macros, plan.daily_calories)


def _collect_user_plan():
    print("Masukkan data personal")
    age = _prompt_int("Umur (tahun): ", min_value=1, max_value=120)
    weight = _prompt_float("Berat badan (kg): ", min_value=20, max_value=300)
    height = _prompt_float("Tinggi badan (cm): ", min_value=80, max_value=250)

    print("\nPilih jenis kelamin")
    print("1. Laki-laki")
    print("2. Perempuan")
    gender = _prompt_choice("Jenis kelamin [1/2]: ", valid_choices=("1", "2"))

    print("\nPilih tujuan diet")
    print("1. Weight loss (diet)")
    print("2. Maintain weight")
    print("3. Muscle gain (bulking)")
    goal = _prompt_choice("Tujuan [1/2/3]: ", valid_choices=("1", "2", "3"))

    print("\nPilih aktivitas harian")
    print("1. Rendah  - jarang olahraga")
    print("2. Sedang  - olahraga 3-5 kali per minggu")
    print("3. Tinggi  - aktivitas fisik berat")
    activity = _prompt_choice("Aktivitas [1/2/3]: ", valid_choices=("1", "2", "3"))

    return build_nutrition_plan(
        age=age,
        weight_kg=weight,
        height_cm=height,
        gender=gender,
        activity=activity,
        goal=goal,
    )


def _print_plan_summary(plan) -> None:
    goal_profile = GOAL_PROFILES[plan.goal_key]
    targets = plan.macro_targets

    print("\n" + "-" * 72)
    print("HASIL PERHITUNGAN")
    print("-" * 72)
    print(f"BMR                         : {plan.bmr:.0f} kcal/hari")
    print(f"Kalori pemeliharaan         : {plan.maintenance_calories:.0f} kcal/hari")
    print(f"Tujuan diet                 : {goal_profile['label']}")
    print(f"Target kalori harian        : {plan.daily_calories:.0f} kcal")
    print("\nTarget makromolekul:")
    print(f"Karbohidrat                 : {targets.carbs:.1f} gram")
    print(f"Protein                     : {targets.protein:.1f} gram")
    print(f"Lemak                       : {targets.fat:.1f} gram")
    print(f"\nCatatan biologis            : {goal_profile['description']}")


def _print_recommended_foods(foods: list[Food], goal_key: str) -> None:
    ranked_foods = rank_foods_by_goal(foods, goal_key, limit=5)
    print("\nMakanan prioritas sesuai tujuan:")
    for index, food in enumerate(ranked_foods, start=1):
        print(
            f"{index}. {food.name} "
            f"({food.calories:.0f} kcal, C {food.carbs:.1f} g, "
            f"P {food.protein:.1f} g, L {food.fat:.1f} g)"
        )


def _print_menu(menu_items: list[MenuItem], totals: dict[str, float], target_calories: float) -> None:
    print("\nMenu rekomendasi harian:")
    if not menu_items:
        print("Belum ada menu yang dapat direkomendasikan dari dataset.")
        return

    for item in menu_items:
        print(
            f"- {item.food.name} x{item.servings} porsi "
            f"= {item.total_calories:.0f} kcal "
            f"(C {item.total_carbs:.1f} g, P {item.total_protein:.1f} g, L {item.total_fat:.1f} g)"
        )

    print("\nTotal menu rekomendasi:")
    print(f"Kalori                     : {totals['calories']:.0f} kcal dari target {target_calories:.0f} kcal")
    print(f"Karbohidrat                : {totals['carbs']:.1f} gram")
    print(f"Protein                    : {totals['protein']:.1f} gram")
    print(f"Lemak                      : {totals['fat']:.1f} gram")


def _print_visualizations(plan, actual_totals: dict[str, float]) -> None:
    print("\n" + "-" * 72)
    print("VISUALISASI CLI")
    print("-" * 72)
    print(render_macro_ratio_chart(plan.macro_ratios))
    print()
    print(render_calorie_progress(actual_totals["calories"], plan.daily_calories))
    print()
    print(render_target_vs_actual(plan.macro_targets.as_dict(), actual_totals))


def _run_food_log_if_requested(
    foods: list[Food],
    target_macros: dict[str, float],
    target_calories: float,
) -> None:
    answer = _prompt_choice("\nApakah ingin mencatat makanan yang sudah dimakan? [y/n]: ", ("y", "n"))
    if answer == "n":
        return

    print("\nDaftar makanan:")
    for index, food in enumerate(foods, start=1):
        print(
            f"{index:2}. {food.name:22} "
            f"{food.calories:5.0f} kcal | C {food.carbs:5.1f} g | "
            f"P {food.protein:5.1f} g | L {food.fat:5.1f} g"
        )

    logged_items: list[MenuItem] = []
    print("\nKetik nomor makanan, atau 0 untuk selesai.")
    while True:
        raw_choice = input("Nomor makanan: ").strip()
        if raw_choice in {"", "0", "selesai"}:
            break
        if not raw_choice.isdigit() or not (1 <= int(raw_choice) <= len(foods)):
            print("Nomor makanan tidak valid.")
            continue

        servings = _prompt_int("Jumlah porsi: ", min_value=1, max_value=20)
        logged_items.append(MenuItem(food=foods[int(raw_choice) - 1], servings=servings))

    if not logged_items:
        print("Belum ada catatan makanan.")
        return

    logged_totals = total_nutrition(logged_items)
    print("\nHasil monitoring asupan:")
    print(render_calorie_progress(logged_totals["calories"], target_calories))
    print(render_target_vs_actual(target_macros, logged_totals))
    _print_intake_notes(target_macros, logged_totals, target_calories)


def _print_intake_notes(
    target_macros: dict[str, float],
    totals: dict[str, float],
    target_calories: float,
) -> None:
    print("\nCatatan monitoring:")
    for key, label in (("carbs", "Karbohidrat"), ("protein", "Protein"), ("fat", "Lemak")):
        difference = totals[key] - target_macros[key]
        if abs(difference) <= target_macros[key] * 0.1:
            status = "mendekati target"
        elif difference < 0:
            status = f"kurang {abs(difference):.1f} gram"
        else:
            status = f"lebih {difference:.1f} gram"
        print(f"- {label}: {status}")

    calorie_difference = totals["calories"] - target_calories
    if abs(calorie_difference) <= target_calories * 0.1:
        print("- Kalori: mendekati target harian")
    elif calorie_difference < 0:
        print(f"- Kalori: kurang {abs(calorie_difference):.0f} kcal")
    else:
        print(f"- Kalori: lebih {calorie_difference:.0f} kcal")


def _estimate_max_servings(target_calories: float) -> int:
    return max(12, min(25, round(target_calories / 130)))


def _prompt_int(prompt: str, min_value: int, max_value: int | None = None) -> int:
    while True:
        raw_value = input(prompt).strip()
        try:
            value = int(raw_value)
        except ValueError:
            print("Masukkan angka bulat yang valid.")
            continue

        if value < min_value:
            print(f"Nilai minimal adalah {min_value}.")
            continue
        if max_value is not None and value > max_value:
            print(f"Nilai maksimal adalah {max_value}.")
            continue
        return value


def _prompt_float(prompt: str, min_value: float, max_value: float | None = None) -> float:
    while True:
        raw_value = input(prompt).strip().replace(",", ".")
        try:
            value = float(raw_value)
        except ValueError:
            print("Masukkan angka yang valid.")
            continue

        if value < min_value:
            print(f"Nilai minimal adalah {min_value}.")
            continue
        if max_value is not None and value > max_value:
            print(f"Nilai maksimal adalah {max_value}.")
            continue
        return value


def _prompt_choice(prompt: str, valid_choices: tuple[str, ...]) -> str:
    valid_choice_set = set(valid_choices)
    while True:
        value = input(prompt).strip().lower()
        if value in valid_choice_set:
            return value
        choices = "/".join(valid_choices)
        print(f"Input tidak valid. Pilih salah satu: {choices}.")


if __name__ == "__main__":
    main()
