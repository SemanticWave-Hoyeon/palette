from __future__ import annotations

import numpy as np

from ._color import linear_to_srgb, rgb01_to_oklab, srgb_to_linear

COLORBLIND_MODES = {None, "protanopia", "deuteranopia", "tritanopia", "achromatopsia"}

_MACHADO_100 = {
    "protanopia": np.array(
        [
            [0.152286, 1.052583, -0.204868],
            [0.114503, 0.786281, 0.099216],
            [-0.003882, -0.048116, 1.051998],
        ],
        dtype=float,
    ),
    "deuteranopia": np.array(
        [
            [0.367322, 0.860646, -0.227968],
            [0.280085, 0.672501, 0.047413],
            [-0.011820, 0.042940, 0.968881],
        ],
        dtype=float,
    ),
    "tritanopia": np.array(
        [
            [1.255528, -0.076749, -0.178779],
            [-0.078411, 0.930809, 0.147602],
            [0.004733, 0.691367, 0.303900],
        ],
        dtype=float,
    ),
}


def simulate_colorblind(rgb: np.ndarray, mode: str | None) -> np.ndarray:
    rgb = np.asarray(rgb, dtype=float)
    if mode is None:
        return np.clip(rgb, 0.0, 1.0)
    if mode not in COLORBLIND_MODES:
        raise ValueError(f"Unsupported colorblind mode: {mode!r}.")

    linear = srgb_to_linear(rgb)
    if mode == "achromatopsia":
        luminance = (
            0.2126 * linear[..., 0] + 0.7152 * linear[..., 1] + 0.0722 * linear[..., 2]
        )
        simulated_linear = np.stack([luminance, luminance, luminance], axis=-1)
    else:
        simulated_linear = linear @ _MACHADO_100[mode].T

    return np.clip(linear_to_srgb(simulated_linear), 0.0, 1.0)


def simulated_oklab(rgb: np.ndarray, mode: str | None) -> np.ndarray:
    return rgb01_to_oklab(simulate_colorblind(rgb, mode))
