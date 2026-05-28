"""Visualisasi hasil rekomendasi untuk antarmuka CLI."""

from __future__ import annotations

from pathlib import Path


MACRO_LABELS = {
    "carbs": "Karbohidrat",
    "protein": "Protein",
    "fat": "Lemak",
}


def render_macro_ratio_chart(ratios: dict[str, float], width: int = 36) -> str:
    lines = ["Komposisi makromolekul target:"]
    for key in ("carbs", "protein", "fat"):
        percentage = ratios[key] * 100
        bar = _bar(ratios[key], width)
        lines.append(f"{MACRO_LABELS[key]:12} | {bar} {percentage:5.1f}%")
    return "\n".join(lines)


def render_target_vs_actual(
    target_macros: dict[str, float],
    actual_macros: dict[str, float],
    width: int = 28,
) -> str:
    lines = ["Perbandingan target vs aktual menu:"]
    for key in ("carbs", "protein", "fat"):
        target = target_macros[key]
        actual = actual_macros.get(key, 0.0)
        ratio = actual / max(target, 1.0)
        bar = _bar(min(ratio, 1.25) / 1.25, width)
        lines.append(
            f"{MACRO_LABELS[key]:12} | {bar} {actual:6.1f} g / {target:6.1f} g"
        )
    return "\n".join(lines)


def render_calorie_progress(actual_calories: float, target_calories: float, width: int = 36) -> str:
    ratio = actual_calories / max(target_calories, 1.0)
    bar = _bar(min(ratio, 1.25) / 1.25, width)
    return f"Kalori       | {bar} {actual_calories:.0f} kcal / {target_calories:.0f} kcal"


def save_png_charts(
    ratios: dict[str, float],
    target_macros: dict[str, float],
    actual_macros: dict[str, float],
    output_dir: str | Path = "output",
) -> tuple[bool, str]:
    """Simpan pie chart dan bar chart jika matplotlib tersedia."""
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return False, "matplotlib belum tersedia, jadi grafik PNG dilewati."

    try:
        path = Path(output_dir)
        path.mkdir(parents=True, exist_ok=True)

        macro_order = ["carbs", "protein", "fat"]
        labels = [MACRO_LABELS[key] for key in macro_order]

        pie_path = path / "pie_makromolekul.png"
        plt.figure(figsize=(6, 5))
        plt.pie([ratios[key] for key in macro_order], labels=labels, autopct="%1.1f%%", startangle=90)
        plt.title("Rasio Makromolekul Target")
        plt.tight_layout()
        plt.savefig(pie_path)
        plt.close()

        bar_path = path / "target_vs_aktual.png"
        target_values = [target_macros[key] for key in macro_order]
        actual_values = [actual_macros.get(key, 0.0) for key in macro_order]
        x_positions = range(len(macro_order))

        plt.figure(figsize=(7, 5))
        plt.bar([x - 0.18 for x in x_positions], target_values, width=0.36, label="Target")
        plt.bar([x + 0.18 for x in x_positions], actual_values, width=0.36, label="Aktual")
        plt.xticks(list(x_positions), labels)
        plt.ylabel("Gram")
        plt.title("Target vs Aktual Makromolekul")
        plt.legend()
        plt.tight_layout()
        plt.savefig(bar_path)
        plt.close()
    except Exception as exc:
        return False, f"Grafik PNG gagal dibuat: {exc}"

    return True, f"Grafik PNG tersimpan di {pie_path} dan {bar_path}."


def _bar(ratio: float, width: int) -> str:
    clamped = max(0.0, min(ratio, 1.0))
    filled = round(clamped * width)
    return "[" + "#" * filled + "." * (width - filled) + "]"
