# Palette

Palette is a Python library and small desktop UI for generating color palettes.
It supports two different workflows:

- `aesthetic`: cohesive palettes for UI, design, and presentation work.
- `categorical`: distinct palettes for papers, charts, and grouped data.

The library returns uppercase `#RRGGBB` strings and can preserve user-supplied
colors while generating compatible remaining colors.

## Installation

```bash
python3 -m pip install -e .
```

For tests:

```bash
python3 -m pip install -e ".[test]"
python3 -m pytest -q
```

## Library Usage

```python
from palette import Palette

Palette(mode="aesthetic", seed=42).generate(n=5)
Palette(mode="categorical", seed=42).generate(n=8)
Palette(mode="aesthetic", seed=42).generate(n=6, seed_colors=["#1E88E5"])
Palette(mode="categorical", colorblind="deuteranopia", seed=42).generate(n=6)
```

Seed colors are preserved at the beginning of the returned palette:

```python
Palette(mode="aesthetic").generate(n=4, seed_colors=["#1E88E5"])
# ["#1E88E5", ...]
```

## Presets

Paper-style categorical presets are available from the public API:

```python
from palette import Palette, list_presets, preset_colors

list_presets()
preset_colors("observable", n=5)
Palette(mode="categorical").preset("nejm", n=10)
```

Included presets:

- `npg`
- `observable`
- `bmj`
- `science`
- `nejm`
- `lancet`
- `jco`

Preset values copied from `#RRGGBBAA` sources are normalized to `#RRGGBB`.
If `n` is larger than a preset, Palette keeps the preset colors first and
generates compatible additional colors.

## Desktop UI

Run the UI with either command:

```bash
palette-ui
```

or during local development:

```bash
python3 palette_ui.py
```

The UI supports:

- setting `n`
- applying presets
- rolling random palettes
- clicking a swatch to lock or unlock it
- double-clicking a swatch to enter a HEX color
- saving the palette as a PNG in `outputs/`
- copying the current palette as a Python array string

When a preset is applied, preset colors are locked in the UI. If `n` is larger
than the preset size, only the original preset colors are locked and the
generated extra colors remain unlocked.

## Algorithm

Palette uses OKLab/OKLCH internally so distances and harmony scores are closer
to visual perception than raw RGB or HSV.

The `aesthetic` mode is score-and-rerank based. It samples many candidate
palettes from analogous and tonal harmony families, then ranks whole palettes
by hue cohesion, lightness contrast, chroma balance, neutral/accent balance,
duplicate avoidance, and penalties for muddy or neon-heavy colors.

The `categorical` mode uses a Glasbey-style greedy farthest-point strategy in
perceptual color space.

Colorblind modes simulate protanopia, deuteranopia, tritanopia, and
achromatopsia, then require generated colors to remain distinguishable after
simulation.

## Development

```bash
python3 -m pip install -e ".[test]"
python3 -m pytest -q
python3 -m compileall -q src palette_ui.py
```

The project intentionally avoids image-generation dependencies for PNG export;
the UI writes simple PNG files with the Python standard library.
