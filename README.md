# Paper Palette

[한국어](README.ko.md) | [日本語](README.ja.md) | [简体中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md)

A lightweight Python tool for generating publication-ready and colorblind-aware
palettes using perceptual color spaces.

Paper Palette is a Python library and small desktop UI for generating color palettes.
It supports two different workflows:

- `aesthetic`: cohesive palettes for UI, design, and presentation work.
- `categorical`: distinct palettes for papers, charts, and grouped data.

The library returns uppercase `#RRGGBB` strings and can preserve user-supplied
colors while generating compatible remaining colors. Generated colors are ordered
by perceptual hue, so neighboring swatches tend to follow a red, orange, yellow,
green, blue, violet-like flow.

## Examples

**Aesthetic palette**

![Aesthetic palette generated with seed 42](docs/assets/aesthetic_seed42.png)

```python
PaperPalette(mode="aesthetic", seed=42).generate(n=6)
```

**Categorical palette**

![Categorical palette generated with seed 42](docs/assets/categorical_seed42.png)

```python
PaperPalette(mode="categorical", seed=42).generate(n=8)
```

**Matplotlib categorical chart examples**

![Matplotlib pie, line, bar, and box plot examples using Paper Palette categorical colors](docs/assets/matplotlib_chart_examples.png)

```python
import matplotlib.pyplot as plt
from paper_palette import PaperPalette

colors = PaperPalette(mode="categorical", seed=73).generate(n=8)

plt.pie([24, 18, 21, 14, 23], colors=colors[:5])
plt.show()
```

**Colorblind-aware categorical palette**

![Deuteranopia-aware categorical palette generated with seed 42](docs/assets/deuteranopia_seed42.png)

```python
PaperPalette(mode="categorical", colorblind="deuteranopia", seed=42).generate(n=6)
```

**Observable preset**

![Observable preset palette](docs/assets/preset_observable.png)

```python
preset_colors("observable")
```

## Features

- Generates cohesive design palettes with `mode="aesthetic"`.
- Generates distinct chart palettes with `mode="categorical"`.
- Extends user-supplied colors while preserving them.
- Sorts newly generated colors by OKLCH hue for easier visual scanning.
- Supports colorblind-aware generation.
- Scores categorical colors for color-name separation, grayscale/lightness
  separation, and white or dark background contrast.
- Includes journal-style presets for paper figures.
- Provides a small Tkinter desktop UI.
- Saves palette previews as PNG files without image-library dependencies.

## Installation

Start by downloading the project from GitHub:

```bash
git clone https://github.com/SemanticWave-Hoyeon/paper-palette.git
cd paper-palette
```

Using a virtual environment is recommended:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell, activate it with:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the package from the project root:

```bash
python3 -m pip install -e .
```

This installs the `paper_palette` package and the `paper-palette-ui` command. Editable
installation is recommended while the project is still local or under active
development.

If you prefer installing dependencies explicitly first, use:

```bash
python3 -m pip install -r requirements.txt
python3 -m pip install -e .
```

Check that the library works:

```bash
python3 - <<'PY'
from paper_palette import PaperPalette
print(PaperPalette(mode="categorical", seed=42).generate(n=5))
PY
```

Run the desktop UI:

```bash
paper-palette-ui
```

Install test dependencies when developing:

```bash
python3 -m pip install -r requirements-dev.txt
python3 -m pip install -e .
python3 -m pytest -q
```

## Library Usage

Import the main generator:

```python
from paper_palette import PaperPalette
```

Generate a cohesive design palette:

```python
colors = PaperPalette(mode="aesthetic", seed=42).generate(n=5)
print(colors)
```

![Library usage aesthetic palette](docs/assets/usage_aesthetic_n5.png)

Generate a distinct chart palette:

```python
colors = PaperPalette(mode="categorical", seed=42).generate(n=8)
print(colors)
```

![Library usage categorical palette](docs/assets/categorical_seed42.png)

Generate a colorblind-aware categorical palette:

```python
colors = PaperPalette(
    mode="categorical",
    colorblind="deuteranopia",
    seed=42,
).generate(n=6)
```

![Library usage deuteranopia-aware categorical palette](docs/assets/deuteranopia_seed42.png)

Generate for a dark chart background:

```python
colors = PaperPalette(
    mode="categorical",
    background="dark",
    seed=42,
).generate(n=7)
```

![Library usage dark-background categorical palette](docs/assets/usage_categorical_dark_seed42.png)

Seed colors are preserved at the beginning of the returned palette:

```python
colors = PaperPalette(mode="aesthetic").generate(
    n=4,
    seed_colors=["#1E88E5"],
)
print(colors)
# ["#1E88E5", ...]
```

![Library usage aesthetic palette with a preserved seed color](docs/assets/usage_seed_color_aesthetic.png)

Extend a locked brand or manuscript color into a full chart palette:

```python
colors = PaperPalette(
    mode="categorical",
    colorblind="deuteranopia",
    background="white",
    seed=12,
).generate(
    n=6,
    seed_colors=["#1E88E5", "#D81B60"],
)
```

![Library usage categorical palette extended from seed colors](docs/assets/usage_seed_colors_categorical.png)

Use an accessible color-cycle preset:

```python
from paper_palette import preset_colors

colors = preset_colors("accessible8")
```

![Library usage accessible8 preset palette](docs/assets/usage_accessible8.png)

Supported `mode` values:

- `aesthetic`: visually cohesive palettes for UI, presentation, and design.
- `categorical`: visually distinct palettes for charts and grouped data.

Supported `colorblind` values:

- `None`
- `"protanopia"`
- `"deuteranopia"`
- `"tritanopia"`
- `"achromatopsia"`

Supported `background` values:

- `"white"`
- `"black"`
- `"light"`
- `"dark"`

Invalid input raises `ValueError`. Accepted color inputs include `#RGB`,
`#RRGGBB`, and `#RRGGBBAA`; output is always normalized to uppercase
`#RRGGBB`.

## Choosing A Mode

Use `aesthetic` when the palette should feel like one visual theme:

```python
PaperPalette(mode="aesthetic").generate(n=6)
```

Aesthetic generation defaults to `harmony="stable"`, which intentionally favors
analogous and tonal templates. Wider templates are available when you want more
contrast inside a still-harmonized design palette:

```python
PaperPalette(mode="aesthetic", harmony="expressive").generate(n=6)
PaperPalette(mode="aesthetic", harmony="triadic").generate(n=6)
```

Use `categorical` when each color represents a different group in a figure:

```python
PaperPalette(mode="categorical").generate(n=6)
```

## Presets

Paper-style categorical presets are available from the public API:

```python
from paper_palette import PaperPalette, list_presets, preset_colors

list_presets()
preset_colors("observable", n=5)
PaperPalette(mode="categorical").preset("nejm", n=10)
```

Included presets:

- `npg`
- `observable`
- `bmj`
- `science`
- `nejm`
- `lancet`
- `jco`
- `petroff6`
- `petroff8`
- `petroff10`

Preset values copied from `#RRGGBBAA` sources are normalized to `#RRGGBB`.
If `n` is larger than a preset, Paper Palette keeps the preset colors first and
generates compatible additional colors.

Example:

```python
palette = PaperPalette(mode="categorical", seed=7).preset("nejm", n=10)
print(palette)
# The first 8 colors are the NEJM preset; the last 2 are generated.
```

## API Reference

| API | Purpose |
| --- | --- |
| `PaperPalette(mode="aesthetic", seed=None, colorblind=None, background="white", harmony="stable")` | Main generator. `Palette` is kept as a shorter alias. |
| `.generate(n, seed_colors=None)` | Return exactly `n` colors as uppercase `#RRGGBB` strings. |
| `.preset(name, n=None, extend=True)` | Return a named preset. If `n` is larger than the preset and `extend=True`, compatible colors are generated after the preset colors. |
| `list_presets()` | Return available preset names. |
| `preset_colors(name, n=None)` | Return normalized colors for a preset. |

`seed` makes generation reproducible. `seed_colors` are preserved at the front
of the result, while newly generated colors after them are sorted by perceptual
hue. Invalid colors or invalid sizes raise `ValueError`.

`harmony` affects `mode="aesthetic"` only. Supported values are `stable`,
`expressive`, `analogous`, `monochrome_accent`, `split_complementary`, and
`triadic`. The default `stable` setting keeps split-complementary and triadic
templates disabled because they often feel less cohesive in small UI or
presentation palettes. Use `expressive` or an exact template name when that
wider color relationship is desired.

## Comparison Example

The figure below compares a common Matplotlib categorical palette with Paper
Palette's categorical output, a colorblind-aware output, and the Petroff
accessible color-cycle preset. It also shows deuteranopia simulation and a
grayscale strip so separability is easier to inspect.

![Matplotlib tab10 compared with Paper Palette categorical palettes](docs/assets/comparison_matplotlib.png)

Paper Palette is not intended to replace full color science packages such as
`colorspace`. It aims to make publication-ready categorical palettes, preset
extension, and a lightweight locking UI easy to use from a small Python package.

See [docs/QUALITY.md](docs/QUALITY.md) for measured OKLab separation,
colorblind-simulation separation, background contrast, and runtime checks.

## Desktop UI

![Paper Palette desktop UI with the Observable preset applied](docs/assets/desktop_ui.png)

Run the UI with either command:

```bash
paper-palette-ui
```

or during local development:

```bash
python3 paper_palette_ui.py
# Legacy filename also works:
python3 palette_ui.py
```

The UI supports:

- setting `n`
- applying presets
- rolling random palettes
- choosing a white, light, black, or dark target background
- clicking a swatch to lock or unlock it
- double-clicking a swatch to enter a HEX color
- saving the palette as a PNG in `outputs/`
- copying the current palette as a Python array string

When a preset is applied, preset colors are locked in the UI. If `n` is larger
than the preset size, only the original preset colors are locked and the
generated extra colors remain unlocked. Rolling without locked colors displays
the generated palette in hue order; when some swatches are locked, their
positions are preserved and only the regenerated swatches are hue-sorted.

Typical UI workflow:

1. Set `n`.
2. Choose a mode.
3. Apply a preset or roll a random palette.
4. Click any swatch to lock it.
5. Roll again to regenerate only unlocked swatches.
6. Double-click a swatch to type a HEX color manually.
7. Save the palette PNG or copy the Python array string.

## Algorithm

Paper Palette uses OKLab/OKLCH internally so distances and harmony scores are closer
to visual perception than raw RGB or HSV.

The `aesthetic` mode is score-and-rerank based. It samples many candidate
palettes from analogous and tonal harmony families by default, then ranks whole
palettes by hue cohesion, lightness contrast, chroma balance, neutral/accent
balance, duplicate avoidance, and penalties for muddy or neon-heavy colors.
Split-complementary and triadic templates are implemented but kept out of the
default `stable` template mix; they can be enabled with `harmony="expressive"`
or selected directly with `harmony="split_complementary"` or `harmony="triadic"`.

The `categorical` mode uses a Glasbey-style greedy farthest-point strategy in
perceptual color space. Its score also rewards color-name separation inspired by
Colorgorical-style work, pairwise lightness separation for grayscale printing,
and contrast against the selected `background`. After greedy selection, a short
local refinement pass tries candidate swaps and keeps only improvements to the
whole-palette score.

After generation, Paper Palette sorts generated colors by OKLCH hue. This does
not change which colors were selected; it only makes the returned list and UI
swatches easier to read from warm colors through greens and blues to violets.
Seed colors and preset colors keep their documented positions.

Colorblind modes simulate protanopia, deuteranopia, tritanopia, and
achromatopsia, then require generated colors to remain distinguishable after
simulation.

See [REFERENCES.md](REFERENCES.md) for the algorithmic sources and how they map
to this implementation.

## License

Paper Palette is released under the [MIT License](LICENSE).

MIT is a good fit for this project because it is a short permissive license that
allows use, modification, distribution, and commercial use while requiring the
copyright and license notice to be preserved.

## Development

```bash
python3 -m pip install -r requirements-dev.txt
python3 -m pip install -e .
python3 -m pytest -q
python3 -m compileall -q src paper_palette_ui.py palette_ui.py
python3 -m build
python3 -m twine check dist/*
```

The project intentionally avoids image-generation dependencies for PNG export;
the UI writes simple PNG files with the Python standard library.
