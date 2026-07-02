import re

import numpy as np
import pytest

from palette import Palette, list_presets, preset_colors
from palette._color import circular_mean_degrees, hex_to_rgb01, hue_distance, normalize_hex, oklab_to_oklch, rgb01_to_oklab
from palette._colorblind import simulated_oklab
from palette._png import save_palette_png
from palette._ui import COLORBLIND_OPTIONS, PRESET_OPTIONS, PaletteApp, preset_palette_state


HEX_RE = re.compile(r"^#[0-9A-F]{6}$")


def test_normalize_hex_accepts_short_and_long_forms():
    assert normalize_hex("#abc") == "#AABBCC"
    assert normalize_hex("1e88e5") == "#1E88E5"
    assert normalize_hex("#4269D0FF") == "#4269D0"


@pytest.mark.parametrize("value", ["", "blue", "#12", "#12345G", 123])
def test_normalize_hex_rejects_invalid_values(value):
    with pytest.raises(ValueError):
        normalize_hex(value)


def test_import_smoke():
    from palette import Palette as ImportedPalette

    assert ImportedPalette is Palette


def test_generate_returns_requested_number_of_hex_colors():
    colors = Palette(mode="aesthetic", seed=7).generate(n=5)
    assert len(colors) == 5
    assert all(HEX_RE.match(color) for color in colors)


def test_generate_is_reproducible_with_same_seed():
    first = Palette(mode="categorical", seed=11).generate(n=6)
    second = Palette(mode="categorical", seed=11).generate(n=6)
    assert first == second


def test_seed_colors_are_preserved_at_front():
    colors = Palette(mode="aesthetic", seed=3).generate(
        n=5,
        seed_colors=["#1e88e5", "#ffc107"],
    )
    assert colors[:2] == ["#1E88E5", "#FFC107"]
    assert len(colors) == 5


def test_preset_colors_are_public_and_normalized():
    assert "npg" in list_presets()
    assert preset_colors("obs", n=3) == ["#4269D0", "#EFB118", "#FF725C"]
    assert Palette(mode="categorical", seed=5).preset("nejm", n=3) == [
        "#BC3C29",
        "#0072B5",
        "#E18727",
    ]


def test_palette_preset_can_extend_beyond_preset_size():
    colors = Palette(mode="categorical", seed=5).preset("nejm", n=10)
    assert colors[:8] == preset_colors("nejm")
    assert len(colors) == 10
    assert all(HEX_RE.match(color) for color in colors)


def test_invalid_constructor_values_raise():
    with pytest.raises(ValueError):
        Palette(mode="random")
    with pytest.raises(ValueError):
        Palette(colorblind="unknown")


def test_invalid_generate_values_raise():
    palette = Palette()
    with pytest.raises(ValueError):
        palette.generate(0)
    with pytest.raises(ValueError):
        palette.generate(1, seed_colors=["#000000", "#FFFFFF"])
    with pytest.raises(ValueError):
        palette.generate(2, seed_colors=["#000000", "#000"])


def test_modes_produce_different_palettes_with_same_seed():
    aesthetic = Palette(mode="aesthetic", seed=19).generate(n=6)
    categorical = Palette(mode="categorical", seed=19).generate(n=6)
    assert aesthetic != categorical


def test_aesthetic_palette_stays_in_a_cohesive_hue_family():
    colors = Palette(mode="aesthetic", seed=42).generate(n=6)
    lab = rgb01_to_oklab(np.array([hex_to_rgb01(color) for color in colors]))
    lch = oklab_to_oklch(lab)
    center = circular_mean_degrees(lch[:, 2])
    assert hue_distance(lch[:, 2], center).max() < 65.0


def test_categorical_palette_has_perceptual_separation():
    colors = Palette(mode="categorical", seed=23).generate(n=8)
    lab = rgb01_to_oklab(np.array([hex_to_rgb01(color) for color in colors]))
    distances = np.linalg.norm(lab[:, None, :] - lab[None, :, :], axis=-1)
    distances[distances == 0] = np.inf
    assert distances.min() > 0.065


@pytest.mark.parametrize("mode", ["protanopia", "deuteranopia", "tritanopia", "achromatopsia"])
def test_colorblind_modes_keep_simulated_colors_apart(mode):
    colors = Palette(mode="categorical", colorblind=mode, seed=31).generate(n=5)
    rgb = np.array([hex_to_rgb01(color) for color in colors])
    lab = simulated_oklab(rgb, mode)
    distances = np.linalg.norm(lab[:, None, :] - lab[None, :, :], axis=-1)
    distances[distances == 0] = np.inf
    assert distances.min() > 0.045


def test_ui_colorblind_options_match_palette_modes():
    assert COLORBLIND_OPTIONS["None"] is None
    for label, mode in COLORBLIND_OPTIONS.items():
        if label == "None":
            continue
        Palette(colorblind=mode)


def test_ui_preset_options_match_public_presets():
    assert PRESET_OPTIONS["None"] is None
    assert set(PRESET_OPTIONS.values()) == {None, *list_presets()}


def test_ui_preset_state_locks_only_preset_colors_when_n_is_larger():
    colors, locked = preset_palette_state(
        preset_name="nejm",
        n=10,
        mode="categorical",
        colorblind=None,
    )
    assert colors[:8] == preset_colors("nejm")
    assert len(colors) == 10
    assert locked == [True] * 8 + [False] * 2


def test_ui_preset_state_locks_all_visible_colors_when_n_fits_preset():
    colors, locked = preset_palette_state(
        preset_name="npg",
        n=6,
        mode="categorical",
        colorblind=None,
    )
    assert colors == preset_colors("npg", n=6)
    assert locked == [True] * 6


def test_ui_text_color_uses_readable_contrast():
    assert PaletteApp._text_color("#FFFFFF") == "#111111"
    assert PaletteApp._text_color("#000000") == "#FFFFFF"
    assert PaletteApp._text_color(None) == "#333333"


def test_save_palette_png_writes_valid_png(tmp_path):
    output = save_palette_png(["#1E88E5", "#FFC107"], tmp_path / "palette.png")
    data = output.read_bytes()
    assert data.startswith(b"\x89PNG\r\n\x1a\n")
    assert b"IHDR" in data[:32]
    assert output.stat().st_size > 100
