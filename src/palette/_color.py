from __future__ import annotations

import math
import re

import numpy as np

HEX_RE = re.compile(r"^#?([0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")


def normalize_hex(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"Expected a HEX color string, got {type(value).__name__}.")

    match = HEX_RE.match(value.strip())
    if not match:
        raise ValueError(f"Invalid HEX color: {value!r}.")

    body = match.group(1)
    if len(body) == 3:
        body = "".join(channel * 2 for channel in body)
    elif len(body) == 8:
        body = body[:6]
    return f"#{body.upper()}"


def hex_to_rgb01(value: str) -> np.ndarray:
    normalized = normalize_hex(value)
    return np.array(
        [int(normalized[i : i + 2], 16) / 255.0 for i in (1, 3, 5)],
        dtype=float,
    )


def rgb01_to_hex(rgb: np.ndarray) -> str:
    clipped = np.clip(np.asarray(rgb, dtype=float), 0.0, 1.0)
    channels = np.rint(clipped * 255).astype(int)
    return f"#{channels[0]:02X}{channels[1]:02X}{channels[2]:02X}"


def srgb_to_linear(rgb: np.ndarray) -> np.ndarray:
    rgb = np.asarray(rgb, dtype=float)
    return np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)


def linear_to_srgb(rgb: np.ndarray) -> np.ndarray:
    rgb = np.asarray(rgb, dtype=float)
    srgb = np.empty_like(rgb, dtype=float)
    low = rgb <= 0.0031308
    srgb[low] = 12.92 * rgb[low]
    srgb[~low] = 1.055 * np.power(rgb[~low], 1 / 2.4) - 0.055
    return srgb


def rgb01_to_oklab(rgb: np.ndarray) -> np.ndarray:
    linear = srgb_to_linear(rgb)
    r, g, b = np.moveaxis(linear, -1, 0)

    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b

    l_, m_, s_ = np.cbrt(l), np.cbrt(m), np.cbrt(s)

    lab = np.stack(
        [
            0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
            1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_,
            0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_,
        ],
        axis=-1,
    )
    return lab


def oklab_to_rgb01(lab: np.ndarray) -> np.ndarray:
    lab = np.asarray(lab, dtype=float)
    L, a, b = np.moveaxis(lab, -1, 0)

    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b

    l, m, s = l_**3, m_**3, s_**3

    linear = np.stack(
        [
            +4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
            -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
            -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s,
        ],
        axis=-1,
    )
    return linear_to_srgb(linear)


def oklab_to_oklch(lab: np.ndarray) -> np.ndarray:
    lab = np.asarray(lab, dtype=float)
    L = lab[..., 0]
    a = lab[..., 1]
    b = lab[..., 2]
    C = np.sqrt(a * a + b * b)
    h = (np.degrees(np.arctan2(b, a)) + 360.0) % 360.0
    return np.stack([L, C, h], axis=-1)


def oklch_to_oklab(lch: np.ndarray) -> np.ndarray:
    lch = np.asarray(lch, dtype=float)
    L = lch[..., 0]
    C = lch[..., 1]
    h = np.radians(lch[..., 2])
    return np.stack([L, C * np.cos(h), C * np.sin(h)], axis=-1)


def hex_to_oklab(value: str) -> np.ndarray:
    return rgb01_to_oklab(hex_to_rgb01(value))


def hex_to_oklch(value: str) -> np.ndarray:
    return oklab_to_oklch(hex_to_oklab(value))


def oklch_to_rgb01_if_in_gamut(lch: np.ndarray, tolerance: float = 1e-7) -> np.ndarray:
    rgb = oklab_to_rgb01(oklch_to_oklab(lch))
    rgb = np.asarray(rgb, dtype=float)
    mask = np.all((rgb >= -tolerance) & (rgb <= 1.0 + tolerance), axis=-1)
    return np.clip(rgb[mask], 0.0, 1.0)


def circular_mean_degrees(values: np.ndarray) -> float:
    radians = np.radians(np.asarray(values, dtype=float))
    x = np.cos(radians).mean()
    y = np.sin(radians).mean()
    if abs(x) < 1e-12 and abs(y) < 1e-12:
        return 0.0
    return float((math.degrees(math.atan2(y, x)) + 360.0) % 360.0)


def hue_distance(a: np.ndarray | float, b: np.ndarray | float) -> np.ndarray:
    return np.abs((np.asarray(a) - np.asarray(b) + 180.0) % 360.0 - 180.0)


def pairwise_min_distance(lab: np.ndarray, selected: np.ndarray) -> np.ndarray:
    if selected.size == 0:
        return np.full((len(lab),), np.inf)
    distances = np.linalg.norm(lab[:, None, :] - selected[None, :, :], axis=-1)
    return distances.min(axis=1)
