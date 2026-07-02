from __future__ import annotations

import statistics
import time
from math import ceil

import numpy as np

from paper_palette import PaperPalette
from paper_palette._color import hex_to_rgb01, rgb01_to_oklab, srgb_to_linear
from paper_palette._colorblind import simulated_oklab


COUNTS = (3, 5, 8, 10, 20)
SEEDS = tuple(range(12))
COLORBLIND_MODES = ("protanopia", "deuteranopia", "tritanopia", "achromatopsia")


def main() -> None:
    print("# Paper Palette Quality and Performance Report")
    print()
    print(f"Seeds: {SEEDS[0]}-{SEEDS[-1]}")
    print()
    print("## Categorical OKLab Separation and Runtime")
    print()
    print("| n | mean min OKLab distance | worst min OKLab distance | mean runtime ms | p95 runtime ms |")
    print("| --- | ---: | ---: | ---: | ---: |")
    for count in COUNTS:
        distances: list[float] = []
        runtimes: list[float] = []
        for seed in SEEDS:
            start = time.perf_counter()
            colors = PaperPalette(mode="categorical", seed=seed).generate(n=count)
            runtimes.append((time.perf_counter() - start) * 1000.0)
            distances.append(min_oklab_distance(colors))
        print(
            f"| {count} | {statistics.mean(distances):.4f} | {min(distances):.4f} | "
            f"{statistics.mean(runtimes):.1f} | {percentile(runtimes, 0.95):.1f} |"
        )

    print()
    print("## Colorblind Simulated Separation")
    print()
    print("| mode | n | mean min simulated OKLab distance | worst min simulated OKLab distance |")
    print("| --- | ---: | ---: | ---: |")
    for mode in COLORBLIND_MODES:
        distances = []
        for seed in SEEDS:
            colors = PaperPalette(mode="categorical", colorblind=mode, seed=seed).generate(n=8)
            distances.append(min_simulated_oklab_distance(colors, mode))
        print(f"| {mode} | 8 | {statistics.mean(distances):.4f} | {min(distances):.4f} |")

    print()
    print("## Background Contrast")
    print()
    print("| target background | n | mean minimum contrast ratio | worst minimum contrast ratio |")
    print("| --- | ---: | ---: | ---: |")
    for background in ("white", "black"):
        ratios = []
        for seed in SEEDS:
            colors = PaperPalette(mode="categorical", background=background, seed=seed).generate(n=8)
            ratios.append(min_contrast_ratio(colors, background))
        print(f"| {background} | 8 | {statistics.mean(ratios):.2f} | {min(ratios):.2f} |")


def min_oklab_distance(colors: list[str]) -> float:
    lab = rgb01_to_oklab(np.array([hex_to_rgb01(color) for color in colors]))
    distances = np.linalg.norm(lab[:, None, :] - lab[None, :, :], axis=-1)
    distances[distances == 0] = np.inf
    return float(distances.min())


def min_simulated_oklab_distance(colors: list[str], mode: str) -> float:
    rgb = np.array([hex_to_rgb01(color) for color in colors])
    lab = simulated_oklab(rgb, mode)
    distances = np.linalg.norm(lab[:, None, :] - lab[None, :, :], axis=-1)
    distances[distances == 0] = np.inf
    return float(distances.min())


def min_contrast_ratio(colors: list[str], background: str) -> float:
    bg_luminance = 1.0 if background == "white" else 0.0
    return min(contrast_ratio(relative_luminance(hex_to_rgb01(color)), bg_luminance) for color in colors)


def relative_luminance(rgb: np.ndarray) -> float:
    linear = srgb_to_linear(rgb)
    return float(0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2])


def contrast_ratio(a: float, b: float) -> float:
    lighter = max(a, b)
    darker = min(a, b)
    return (lighter + 0.05) / (darker + 0.05)


def percentile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, ceil((len(ordered) - 1) * q)))
    return ordered[index]


if __name__ == "__main__":
    main()
