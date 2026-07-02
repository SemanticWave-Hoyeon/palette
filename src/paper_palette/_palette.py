from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ._color import (
    circular_mean_degrees,
    hex_to_rgb01,
    hue_distance,
    normalize_hex,
    oklab_to_oklch,
    oklch_to_rgb01_if_in_gamut,
    pairwise_min_distance,
    rgb01_to_hex,
    rgb01_to_oklab,
)
from ._colorblind import COLORBLIND_MODES, simulated_oklab
from ._presets import preset_colors

MODES = {"aesthetic", "categorical"}
BACKGROUNDS = {"white", "black", "light", "dark"}
HUE_SORT_START_DEGREES = 350.0
NEUTRAL_CHROMA_THRESHOLD = 0.035


@dataclass(frozen=True)
class _CandidatePool:
    rgb: np.ndarray
    lab: np.ndarray
    lch: np.ndarray
    simulated_lab: np.ndarray


class Palette:
    """Generate perceptual color palettes for design and categorical charts."""

    def __init__(
        self,
        mode: str = "aesthetic",
        seed: int | None = None,
        colorblind: str | None = None,
        background: str = "white",
    ) -> None:
        if mode not in MODES:
            raise ValueError("mode must be 'aesthetic' or 'categorical'.")
        if colorblind not in COLORBLIND_MODES:
            supported = ", ".join(repr(item) for item in sorted(m for m in COLORBLIND_MODES if m))
            raise ValueError(f"colorblind must be None or one of: {supported}.")
        if background not in BACKGROUNDS:
            supported = ", ".join(repr(item) for item in sorted(BACKGROUNDS))
            raise ValueError(f"background must be one of: {supported}.")

        self.mode = mode
        self.seed = seed
        self.colorblind = colorblind
        self.background = background
        self._rng = np.random.default_rng(seed)

    def generate(self, n: int, seed_colors: list[str] | tuple[str, ...] | None = None) -> list[str]:
        if not isinstance(n, int):
            raise ValueError("n must be an integer.")
        if n <= 0:
            raise ValueError("n must be greater than 0.")

        normalized = [normalize_hex(color) for color in seed_colors or []]
        if len(normalized) > n:
            raise ValueError("seed_colors cannot contain more colors than n.")
        if len(set(normalized)) != len(normalized):
            raise ValueError("seed_colors cannot contain duplicate colors.")
        if len(normalized) == n:
            return normalized

        seed_rgb = np.array([hex_to_rgb01(color) for color in normalized], dtype=float)
        seed_lab = rgb01_to_oklab(seed_rgb) if len(seed_rgb) else np.empty((0, 3), dtype=float)
        seed_lch = oklab_to_oklch(seed_lab) if len(seed_lab) else np.empty((0, 3), dtype=float)
        seed_sim_lab = (
            simulated_oklab(seed_rgb, self.colorblind)
            if len(seed_rgb)
            else np.empty((0, 3), dtype=float)
        )

        if self.mode == "aesthetic":
            generated_rgb = self._generate_aesthetic(n - len(normalized), seed_lab, seed_lch, seed_sim_lab)
        else:
            generated_rgb = self._generate_categorical(
                n - len(normalized),
                seed_lab,
                seed_lch,
                seed_sim_lab,
            )

        generated = _sort_generated_colors([rgb01_to_hex(rgb) for rgb in generated_rgb])
        return normalized + generated

    def preset(self, name: str, n: int | None = None, extend: bool = True) -> list[str]:
        colors = preset_colors(name)
        if n is None:
            return colors
        if not isinstance(n, int):
            raise ValueError("n must be an integer.")
        if n <= 0:
            raise ValueError("n must be greater than 0.")
        if n <= len(colors):
            return colors[:n]
        if not extend:
            raise ValueError(f"Preset {name!r} has only {len(colors)} colors.")
        return self.generate(n=n, seed_colors=colors)

    def _generate_aesthetic(
        self,
        count: int,
        seed_lab: np.ndarray,
        seed_lch: np.ndarray,
        seed_sim_lab: np.ndarray,
    ) -> np.ndarray:
        attempts = max(96, 28 * (count + len(seed_lab)))
        best_score = -np.inf
        best_rgb: np.ndarray | None = None

        for _ in range(attempts):
            generated_rgb, template, hue_centers = self._aesthetic_candidate(
                count,
                seed_lab,
                seed_lch,
                seed_sim_lab,
            )
            generated_lab = rgb01_to_oklab(generated_rgb)
            generated_lch = oklab_to_oklch(generated_lab)
            generated_sim_lab = simulated_oklab(generated_rgb, self.colorblind)

            full_lab = np.vstack([seed_lab, generated_lab]) if len(seed_lab) else generated_lab
            full_lch = np.vstack([seed_lch, generated_lch]) if len(seed_lch) else generated_lch
            full_sim_lab = (
                np.vstack([seed_sim_lab, generated_sim_lab])
                if len(seed_sim_lab)
                else generated_sim_lab
            )
            score = self._aesthetic_palette_score(full_lab, full_lch, full_sim_lab, hue_centers, template)
            score += float(self._rng.normal(0.0, 0.003))
            if score > best_score:
                best_score = score
                best_rgb = generated_rgb

        if best_rgb is None:
            raise RuntimeError("Could not generate an aesthetic palette.")
        return best_rgb

    def _aesthetic_candidate(
        self,
        count: int,
        seed_lab: np.ndarray,
        seed_lch: np.ndarray,
        seed_sim_lab: np.ndarray,
    ) -> tuple[np.ndarray, str, np.ndarray]:
        base_hue = (
            circular_mean_degrees(seed_lch[:, 2])
            if len(seed_lch)
            else float(self._rng.uniform(0.0, 360.0))
        )
        target_l = float(np.clip(seed_lch[:, 0].mean(), 0.50, 0.78)) if len(seed_lch) else 0.66
        target_c = float(np.clip(seed_lch[:, 1].mean(), 0.07, 0.19)) if len(seed_lch) else 0.13
        template = self._choose_harmony_template(count, bool(len(seed_lch)))
        hue_centers = self._harmony_hues(base_hue, template)
        lightness_window = self._aesthetic_lightness_window(target_l, template)
        chroma_window = self._aesthetic_chroma_window(target_c, template)

        pool = self._candidate_pool(
            size=max(900, 360 * count),
            hue_centers=hue_centers,
            hue_sigma=12.0 if template in {"analogous", "monochrome_accent"} else 16.0,
            lightness=lightness_window,
            chroma=chroma_window,
        )

        selected_rgb: list[np.ndarray] = []
        selected_lab = seed_lab.copy()
        selected_sim_lab = seed_sim_lab.copy()

        for step in range(count):
            normal_min = pairwise_min_distance(pool.lab, selected_lab)
            sim_min = pairwise_min_distance(pool.simulated_lab, selected_sim_lab)
            used = np.array(selected_rgb, dtype=float)
            used_lab = rgb01_to_oklab(used) if len(used) else np.empty((0, 3), dtype=float)
            if len(used_lab):
                normal_min = np.minimum(normal_min, pairwise_min_distance(pool.lab, used_lab))

            threshold = self._distance_threshold("aesthetic", len(seed_lab) + step + 1)
            valid = normal_min > 0.030
            if self.colorblind is not None:
                valid &= sim_min > threshold

            hue_fit = self._template_distance(pool.lch[:, 2], hue_centers)
            lightness_fit = np.abs(pool.lch[:, 0] - target_l)
            chroma_fit = np.abs(pool.lch[:, 1] - target_c)
            too_close_penalty = np.clip(0.055 - normal_min, 0.0, None) * 6.0
            spacing_bonus = np.minimum(normal_min, 0.16) * 0.55
            role_bonus = self._aesthetic_role_bonus(pool.lch, step, count, template)

            scores = (
                -((hue_fit / 38.0) ** 2) * 1.15
                - lightness_fit * 1.25
                - chroma_fit * 0.85
                - too_close_penalty
                + spacing_bonus
                + role_bonus
            )
            scores += self._rng.normal(0.0, 0.045, size=len(scores))
            scores[~valid] = -np.inf
            choice = self._best_available(scores)

            rgb = pool.rgb[choice]
            selected_rgb.append(rgb)
            selected_lab = np.vstack([selected_lab, pool.lab[choice]])
            selected_sim_lab = np.vstack([selected_sim_lab, pool.simulated_lab[choice]])

        return np.array(selected_rgb, dtype=float), template, hue_centers

    @staticmethod
    def _aesthetic_lightness_window(target_l: float, template: str) -> tuple[float, float]:
        if template == "monochrome_accent":
            spread = 0.22
        elif template == "analogous":
            spread = 0.18
        else:
            spread = 0.16
        return max(0.40, target_l - spread), min(0.86, target_l + spread)

    @staticmethod
    def _aesthetic_chroma_window(target_c: float, template: str) -> tuple[float, float]:
        if template == "monochrome_accent":
            low, high = target_c - 0.075, target_c + 0.090
        elif template == "analogous":
            low, high = target_c - 0.060, target_c + 0.075
        else:
            low, high = target_c - 0.050, target_c + 0.065
        return max(0.065, low), min(0.215, high)

    @staticmethod
    def _aesthetic_role_bonus(
        lch: np.ndarray,
        step: int,
        count: int,
        template: str,
    ) -> np.ndarray:
        lightness = lch[:, 0]
        chroma = lch[:, 1]

        if count <= 1:
            desired_l = 0.66
        else:
            desired_l = np.linspace(0.78, 0.50, count)[step]
        lightness_role = -np.abs(lightness - desired_l) * 0.20

        moderate_chroma = -np.abs(chroma - 0.145) * 0.22
        if template == "monochrome_accent" and step == count - 1:
            accent = np.clip(chroma - 0.135, 0.0, 0.08) * 0.90
        else:
            accent = np.zeros_like(chroma)

        return lightness_role + moderate_chroma + accent

    def _aesthetic_palette_score(
        self,
        lab: np.ndarray,
        lch: np.ndarray,
        simulated_lab_values: np.ndarray,
        hue_centers: np.ndarray,
        template: str,
    ) -> float:
        if len(lab) == 0:
            return -np.inf

        lightness = lch[:, 0]
        chroma = lch[:, 1]
        template_dist = self._template_distance(lch[:, 2], hue_centers)
        pairwise = self._pairwise_distances(lab)

        hue_harmony = -float(np.mean((template_dist / 34.0) ** 2)) * 1.50
        lightness_range = float(lightness.max() - lightness.min())
        target_range = 0.17 if template in {"analogous", "monochrome_accent"} else 0.14
        lightness_contrast = -abs(lightness_range - target_range) * 2.20
        lightness_balance = -abs(float(lightness.mean()) - 0.66) * 0.85
        lightness_penalty = -float(np.mean(np.clip(0.43 - lightness, 0.0, None))) * 4.0
        lightness_penalty -= float(np.mean(np.clip(lightness - 0.86, 0.0, None))) * 4.0

        chroma_mean = float(chroma.mean())
        chroma_std = float(chroma.std())
        chroma_balance = -abs(chroma_mean - 0.145) * 1.40 - abs(chroma_std - 0.035) * 0.75
        neon_penalty = -float(np.mean(np.clip(chroma - 0.205, 0.0, None))) * 4.8
        muddy_penalty = -float(np.mean(np.clip(0.075 - chroma, 0.0, None))) * 5.0
        muddy_penalty += self._muddy_hue_penalty(lch)

        if len(lab) > 1:
            min_distance = float(pairwise.min())
            mean_distance = float(pairwise.mean())
        else:
            min_distance = 0.08
            mean_distance = 0.12
        separation = min(min_distance, 0.10) * 1.15
        cohesion = -max(mean_distance - 0.215, 0.0) * 1.65
        near_duplicate_penalty = -max(0.032 - min_distance, 0.0) * 7.0

        role_balance = self._aesthetic_role_balance(chroma, lightness)

        colorblind_score = 0.0
        if self.colorblind is not None and len(simulated_lab_values) > 1:
            sim_pairwise = self._pairwise_distances(simulated_lab_values)
            sim_min = float(sim_pairwise.min())
            threshold = self._distance_threshold("aesthetic", len(simulated_lab_values))
            colorblind_score = -max(threshold - sim_min, 0.0) * 8.0 + min(sim_min, 0.08) * 0.25

        return (
            hue_harmony
            + lightness_contrast
            + lightness_balance
            + lightness_penalty
            + chroma_balance
            + neon_penalty
            + muddy_penalty
            + separation
            + cohesion
            + near_duplicate_penalty
            + role_balance
            + colorblind_score
        )

    @staticmethod
    def _aesthetic_role_balance(chroma: np.ndarray, lightness: np.ndarray) -> float:
        if len(chroma) < 3:
            return 0.0

        accents = int(np.count_nonzero(chroma >= 0.155))
        quiet = int(np.count_nonzero(chroma <= 0.105))
        soft_light = int(np.count_nonzero(lightness >= 0.74))
        deep = int(np.count_nonzero(lightness <= 0.55))

        score = 0.0
        score += 0.050 if 1 <= accents <= max(2, len(chroma) // 3) else -0.060
        score += 0.018 if quiet >= 1 else 0.0
        score += 0.025 if soft_light >= 1 else 0.0
        score += 0.025 if deep >= 1 and len(chroma) >= 5 else 0.0
        return score

    @staticmethod
    def _muddy_hue_penalty(lch: np.ndarray) -> float:
        lightness = lch[:, 0]
        chroma = lch[:, 1]
        hue = lch[:, 2]

        yellow_green = hue_distance(hue, 95.0) < 36.0
        brown_or_olive = hue_distance(hue, 62.0) < 30.0
        muddy = (yellow_green | brown_or_olive) & (chroma < 0.135) & (lightness < 0.76)
        return -float(np.count_nonzero(muddy)) * 0.055

    @staticmethod
    def _pairwise_distances(values: np.ndarray) -> np.ndarray:
        distances = np.linalg.norm(values[:, None, :] - values[None, :, :], axis=-1)
        mask = ~np.eye(len(values), dtype=bool)
        return distances[mask]

    def _generate_categorical(
        self,
        count: int,
        seed_lab: np.ndarray,
        seed_lch: np.ndarray,
        seed_sim_lab: np.ndarray,
    ) -> np.ndarray:
        tone_hue = (
            circular_mean_degrees(seed_lch[:, 2])
            if len(seed_lch)
            else float(self._rng.uniform(0.0, 360.0))
        )
        pool = self._candidate_pool(
            size=max(2500, 900 * (count + len(seed_lab))),
            hue_centers=None,
            hue_sigma=None,
            lightness=(0.46, 0.82),
            chroma=(0.075, 0.215),
        )

        selected_rgb: list[np.ndarray] = []
        selected_lab = seed_lab.copy()
        selected_lch = seed_lch.copy()
        selected_sim_lab = seed_sim_lab.copy()

        for step in range(count):
            normal_min = pairwise_min_distance(pool.lab, selected_lab)
            sim_min = pairwise_min_distance(pool.simulated_lab, selected_sim_lab)
            lightness_min = self._min_lightness_distance(pool.lch, selected_lch)
            name_distance = self._color_name_distance(pool.lch, selected_lch)

            if selected_rgb:
                used = np.array(selected_rgb, dtype=float)
                used_lab = rgb01_to_oklab(used)
                used_lch = oklab_to_oklch(used_lab)
                used_sim_lab = simulated_oklab(used, self.colorblind)
                normal_min = np.minimum(normal_min, pairwise_min_distance(pool.lab, used_lab))
                lightness_min = np.minimum(lightness_min, self._min_lightness_distance(pool.lch, used_lch))
                name_distance = np.minimum(name_distance, self._color_name_distance(pool.lch, used_lch))
                sim_min = np.minimum(sim_min, pairwise_min_distance(pool.simulated_lab, used_sim_lab))

            threshold = self._distance_threshold("categorical", len(seed_lab) + step + 1)
            valid = normal_min > threshold
            valid &= lightness_min > self._lightness_threshold(len(seed_lab) + step + 1)
            if self.colorblind is not None:
                valid &= sim_min > threshold

            lightness_fit = 1.0 - np.abs(pool.lch[:, 0] - 0.65) / 0.25
            chroma_fit = 1.0 - np.abs(pool.lch[:, 1] - 0.15) / 0.12
            tone_fit = 1.0 - np.minimum(hue_distance(pool.lch[:, 2], tone_hue), 90.0) / 90.0
            background_fit = self._background_contrast_score(pool.lch)
            name_fit = np.minimum(name_distance, 2.0) / 2.0
            lightness_fit_pairwise = np.minimum(lightness_min, 0.12) / 0.12
            if selected_lab.size:
                distance_score = normal_min
            else:
                distance_score = 0.18 + self._rng.uniform(0.0, 0.02, size=len(pool.rgb))

            scores = (
                distance_score * 1.55
                + np.minimum(sim_min, 0.22) * (0.65 if self.colorblind is not None else 0.15)
                + lightness_fit * 0.08
                + chroma_fit * 0.07
                + tone_fit * 0.035
                + background_fit * 0.060
                + name_fit * 0.055
                + lightness_fit_pairwise * 0.050
            )
            scores[name_distance < 1.0] -= 0.090
            scores[~valid] = -np.inf
            choice = self._best_available(scores)

            rgb = pool.rgb[choice]
            selected_rgb.append(rgb)
            selected_lab = np.vstack([selected_lab, pool.lab[choice]])
            selected_lch = np.vstack([selected_lch, pool.lch[choice]])
            selected_sim_lab = np.vstack([selected_sim_lab, pool.simulated_lab[choice]])

        generated_rgb = np.array(selected_rgb, dtype=float)
        return self._refine_categorical(generated_rgb, seed_lab, seed_lch, seed_sim_lab, pool)

    def _candidate_pool(
        self,
        size: int,
        hue_centers: np.ndarray | None,
        hue_sigma: float | None,
        lightness: tuple[float, float],
        chroma: tuple[float, float],
    ) -> _CandidatePool:
        rgb_chunks: list[np.ndarray] = []
        attempts = 0
        while sum(len(chunk) for chunk in rgb_chunks) < size and attempts < 30:
            attempts += 1
            batch_size = max(size, 1024)
            L = self._rng.uniform(lightness[0], lightness[1], size=batch_size)
            C = self._rng.uniform(chroma[0], chroma[1], size=batch_size)
            if hue_centers is None:
                h = self._rng.uniform(0.0, 360.0, size=batch_size)
            else:
                centers = self._rng.choice(hue_centers, size=batch_size)
                h = (centers + self._rng.normal(0.0, hue_sigma or 1.0, size=batch_size)) % 360.0

            lch = np.stack([L, C, h], axis=-1)
            rgb_chunks.append(oklch_to_rgb01_if_in_gamut(lch))

        if not rgb_chunks:
            raise RuntimeError("Could not generate any in-gamut color candidates.")

        rgb = np.vstack(rgb_chunks)
        if len(rgb) < size:
            raise RuntimeError("Could not generate enough in-gamut color candidates.")
        rgb = rgb[:size]
        lab = rgb01_to_oklab(rgb)
        lch = oklab_to_oklch(lab)
        sim_lab = simulated_oklab(rgb, self.colorblind)
        return _CandidatePool(rgb=rgb, lab=lab, lch=lch, simulated_lab=sim_lab)

    def _choose_harmony_template(self, count: int, has_seed: bool) -> str:
        templates = np.array(["analogous", "monochrome_accent", "split_complementary", "triadic"])
        if has_seed:
            weights = np.array([0.85, 0.15, 0.00, 0.00])
        elif count <= 4:
            weights = np.array([0.76, 0.24, 0.00, 0.00])
        else:
            weights = np.array([0.78, 0.22, 0.00, 0.00])
        return str(self._rng.choice(templates, p=weights))

    @staticmethod
    def _harmony_hues(base_hue: float, template: str) -> np.ndarray:
        if template == "analogous":
            offsets = np.array([-38, -22, -9, 0, 11, 24, 39], dtype=float)
        elif template == "monochrome_accent":
            offsets = np.array([-28, -16, -8, 0, 8, 16, 28], dtype=float)
        elif template == "split_complementary":
            offsets = np.array([-24, -10, 0, 10, 24, 150, 210], dtype=float)
        elif template == "triadic":
            offsets = np.array([-16, 0, 16, 120, 240], dtype=float)
        else:
            raise ValueError(f"Unknown harmony template: {template!r}.")
        return (base_hue + offsets) % 360.0

    @staticmethod
    def _template_distance(hues: np.ndarray, centers: np.ndarray) -> np.ndarray:
        distances = hue_distance(hues[:, None], centers[None, :])
        return distances.min(axis=1)

    @staticmethod
    def _distance_threshold(mode: str, palette_size: int) -> float:
        if mode == "categorical":
            base = 0.070 if palette_size <= 8 else 0.058
        else:
            base = 0.034 if palette_size <= 8 else 0.028
        return base

    @staticmethod
    def _lightness_threshold(palette_size: int) -> float:
        if palette_size <= 6:
            return 0.030
        if palette_size <= 10:
            return 0.020
        return 0.012

    def _background_contrast_score(self, lch: np.ndarray) -> np.ndarray:
        lightness = lch[:, 0]
        if self.background in {"white", "light"}:
            target = 0.66 if self.mode == "aesthetic" else 0.62
            return np.clip((0.88 - lightness) / 0.34, 0.0, 1.0) - np.clip(target - lightness, 0.0, None) * 0.6
        target = 0.70
        return np.clip((lightness - 0.34) / 0.38, 0.0, 1.0) - np.clip(lightness - target, 0.0, None) * 0.4

    @classmethod
    def _min_lightness_distance(cls, lch: np.ndarray, selected_lch: np.ndarray) -> np.ndarray:
        if selected_lch.size == 0:
            return np.full((len(lch),), np.inf)
        return np.abs(lch[:, None, 0] - selected_lch[None, :, 0]).min(axis=1)

    @classmethod
    def _color_name_distance(cls, lch: np.ndarray, selected_lch: np.ndarray) -> np.ndarray:
        if selected_lch.size == 0:
            return np.full((len(lch),), 2.0)

        names = cls._color_name_bins(lch)
        selected_names = cls._color_name_bins(selected_lch)
        distances = np.abs(names[:, None] - selected_names[None, :])
        chromatic = (names[:, None] < 8) & (selected_names[None, :] < 8)
        distances = np.where(chromatic, np.minimum(distances, 8 - distances), distances)
        distances = np.where(names[:, None] == selected_names[None, :], 0, distances)
        return distances.min(axis=1).astype(float)

    @staticmethod
    def _color_name_bins(lch: np.ndarray) -> np.ndarray:
        values = np.asarray(lch, dtype=float)
        lightness = values[..., 0]
        chroma = values[..., 1]
        hue = values[..., 2]
        bins = np.full(lightness.shape, 8, dtype=int)

        neutral = chroma < NEUTRAL_CHROMA_THRESHOLD
        bins[(neutral) & (lightness < 0.35)] = 9
        bins[(neutral) & (lightness >= 0.35) & (lightness <= 0.82)] = 8
        bins[(neutral) & (lightness > 0.82)] = 10

        chromatic = ~neutral
        sector = np.floor(((hue - 15.0) % 360.0) / 45.0).astype(int)
        bins[chromatic] = sector[chromatic]
        return bins

    def _refine_categorical(
        self,
        generated_rgb: np.ndarray,
        seed_lab: np.ndarray,
        seed_lch: np.ndarray,
        seed_sim_lab: np.ndarray,
        pool: _CandidatePool,
    ) -> np.ndarray:
        if len(generated_rgb) <= 1:
            return generated_rgb

        selected_rgb = generated_rgb.copy()
        selected_lab = rgb01_to_oklab(selected_rgb)
        selected_lch = oklab_to_oklch(selected_lab)
        selected_sim_lab = simulated_oklab(selected_rgb, self.colorblind)
        best_score = self._categorical_set_score(
            selected_lab,
            selected_lch,
            selected_sim_lab,
            seed_lab,
            seed_lch,
            seed_sim_lab,
        )

        iterations = min(80, 12 * len(generated_rgb))
        for _ in range(iterations):
            replace_index = int(self._rng.integers(0, len(selected_rgb)))
            keep = np.ones(len(selected_rgb), dtype=bool)
            keep[replace_index] = False

            fixed_lab = np.vstack([seed_lab, selected_lab[keep]]) if len(seed_lab) else selected_lab[keep]
            fixed_lch = np.vstack([seed_lch, selected_lch[keep]]) if len(seed_lch) else selected_lch[keep]
            fixed_sim = (
                np.vstack([seed_sim_lab, selected_sim_lab[keep]])
                if len(seed_sim_lab)
                else selected_sim_lab[keep]
            )

            normal_min = pairwise_min_distance(pool.lab, fixed_lab)
            sim_min = pairwise_min_distance(pool.simulated_lab, fixed_sim)
            lightness_min = self._min_lightness_distance(pool.lch, fixed_lch)
            name_distance = self._color_name_distance(pool.lch, fixed_lch)

            palette_size = len(seed_lab) + len(selected_rgb)
            valid = normal_min > self._distance_threshold("categorical", palette_size)
            valid &= lightness_min > self._lightness_threshold(palette_size)
            if self.colorblind is not None:
                valid &= sim_min > self._distance_threshold("categorical", palette_size)

            candidate_scores = (
                normal_min * 1.40
                + np.minimum(sim_min, 0.22) * (0.70 if self.colorblind is not None else 0.18)
                + np.minimum(lightness_min, 0.12) * 0.40
                + np.minimum(name_distance, 2.0) * 0.035
                + self._background_contrast_score(pool.lch) * 0.045
            )
            candidate_scores[name_distance < 1.0] -= 0.10
            candidate_scores[~valid] = -np.inf
            choice = self._best_available(candidate_scores)

            trial_rgb = selected_rgb.copy()
            trial_rgb[replace_index] = pool.rgb[choice]
            trial_lab = rgb01_to_oklab(trial_rgb)
            trial_lch = oklab_to_oklch(trial_lab)
            trial_sim_lab = simulated_oklab(trial_rgb, self.colorblind)
            trial_score = self._categorical_set_score(
                trial_lab,
                trial_lch,
                trial_sim_lab,
                seed_lab,
                seed_lch,
                seed_sim_lab,
            )
            if trial_score > best_score + 1e-9:
                selected_rgb = trial_rgb
                selected_lab = trial_lab
                selected_lch = trial_lch
                selected_sim_lab = trial_sim_lab
                best_score = trial_score

        return selected_rgb

    def _categorical_set_score(
        self,
        generated_lab: np.ndarray,
        generated_lch: np.ndarray,
        generated_sim_lab: np.ndarray,
        seed_lab: np.ndarray,
        seed_lch: np.ndarray,
        seed_sim_lab: np.ndarray,
    ) -> float:
        lab = np.vstack([seed_lab, generated_lab]) if len(seed_lab) else generated_lab
        lch = np.vstack([seed_lch, generated_lch]) if len(seed_lch) else generated_lch
        sim_lab = np.vstack([seed_sim_lab, generated_sim_lab]) if len(seed_sim_lab) else generated_sim_lab
        if len(lab) <= 1:
            return 0.0

        pairwise = self._pairwise_distances(lab)
        sim_pairwise = self._pairwise_distances(sim_lab)
        min_lightness = self._pairwise_lightness(lch).min()
        name_penalty = self._color_name_duplicate_penalty(lch)
        background_score = float(self._background_contrast_score(lch).mean())
        lightness_balance = -abs(float(lch[:, 0].mean()) - (0.62 if self.background in {"white", "light"} else 0.70))
        return (
            float(pairwise.min()) * 1.80
            + float(pairwise.mean()) * 0.35
            + min(float(sim_pairwise.min()), 0.18) * (0.85 if self.colorblind is not None else 0.20)
            + min(float(min_lightness), 0.12) * 0.75
            + background_score * 0.16
            + lightness_balance * 0.08
            - name_penalty * 0.12
        )

    @staticmethod
    def _pairwise_lightness(lch: np.ndarray) -> np.ndarray:
        distances = np.abs(lch[:, None, 0] - lch[None, :, 0])
        mask = ~np.eye(len(lch), dtype=bool)
        return distances[mask]

    @classmethod
    def _color_name_duplicate_penalty(cls, lch: np.ndarray) -> float:
        names = cls._color_name_bins(lch)
        _, counts = np.unique(names, return_counts=True)
        return float(np.sum(np.clip(counts - 1, 0, None)))

    @staticmethod
    def _best_available(scores: np.ndarray) -> int:
        if np.isfinite(scores).any():
            return int(np.nanargmax(scores))
        return int(np.nanargmax(np.where(np.isnan(scores), -np.inf, scores)))


def _sort_generated_colors(colors: list[str]) -> list[str]:
    """Order generated colors by perceptual hue so neighboring swatches feel related."""
    if len(colors) <= 1:
        return colors

    rgb = np.array([hex_to_rgb01(color) for color in colors], dtype=float)
    lch = oklab_to_oklch(rgb01_to_oklab(rgb))
    order = sorted(range(len(colors)), key=lambda index: _palette_order_key(lch[index]))
    return [colors[index] for index in order]


def _palette_order_key(lch: np.ndarray) -> tuple[int, float, float, float]:
    lightness = float(lch[0])
    chroma = float(lch[1])
    hue = float(lch[2])

    if chroma < NEUTRAL_CHROMA_THRESHOLD:
        return (1, -lightness, 0.0, 0.0)

    hue_position = (hue - HUE_SORT_START_DEGREES) % 360.0
    return (0, hue_position, -chroma, -lightness)
