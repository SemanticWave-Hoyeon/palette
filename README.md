# Palette

Palette is a Python library and small desktop UI for generating color palettes.
It supports two different workflows:

- `aesthetic`: cohesive palettes for UI, design, and presentation work.
- `categorical`: distinct palettes for papers, charts, and grouped data.

The library returns uppercase `#RRGGBB` strings and can preserve user-supplied
colors while generating compatible remaining colors.

## Examples

**Aesthetic palette**

![Aesthetic palette generated with seed 42](docs/assets/aesthetic_seed42.png)

```python
Palette(mode="aesthetic", seed=42).generate(n=6)
```

**Categorical palette**

![Categorical palette generated with seed 42](docs/assets/categorical_seed42.png)

```python
Palette(mode="categorical", seed=42).generate(n=8)
```

**Colorblind-aware categorical palette**

![Deuteranopia-aware categorical palette generated with seed 42](docs/assets/deuteranopia_seed42.png)

```python
Palette(mode="categorical", colorblind="deuteranopia", seed=42).generate(n=6)
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
- Supports colorblind-aware generation.
- Includes journal-style presets for paper figures.
- Provides a small Tkinter desktop UI.
- Saves palette previews as PNG files without image-library dependencies.

## Installation

From the project root:

```bash
python3 -m pip install -e .
```

This installs the `palette` package and the `palette-ui` command. Editable
installation is recommended while the project is still local or under active
development.

Install test dependencies when developing:

```bash
python3 -m pip install -e ".[test]"
python3 -m pytest -q
```

## Library Usage

Import the main generator:

```python
from palette import Palette
```

Generate a cohesive design palette:

```python
colors = Palette(mode="aesthetic", seed=42).generate(n=5)
print(colors)
```

Generate a distinct chart palette:

```python
colors = Palette(mode="categorical", seed=42).generate(n=8)
print(colors)
```

Generate a colorblind-aware categorical palette:

```python
colors = Palette(
    mode="categorical",
    colorblind="deuteranopia",
    seed=42,
).generate(n=6)
```

Seed colors are preserved at the beginning of the returned palette:

```python
colors = Palette(mode="aesthetic").generate(
    n=4,
    seed_colors=["#1E88E5"],
)
print(colors)
# ["#1E88E5", ...]
```

Supported `mode` values:

- `aesthetic`: visually cohesive palettes for UI, presentation, and design.
- `categorical`: visually distinct palettes for charts and grouped data.

Supported `colorblind` values:

- `None`
- `"protanopia"`
- `"deuteranopia"`
- `"tritanopia"`
- `"achromatopsia"`

Invalid input raises `ValueError`. Accepted color inputs include `#RGB`,
`#RRGGBB`, and `#RRGGBBAA`; output is always normalized to uppercase
`#RRGGBB`.

## Choosing A Mode

Use `aesthetic` when the palette should feel like one visual theme:

```python
Palette(mode="aesthetic").generate(n=6)
```

Use `categorical` when each color represents a different group in a figure:

```python
Palette(mode="categorical").generate(n=6)
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

Example:

```python
palette = Palette(mode="categorical", seed=7).preset("nejm", n=10)
print(palette)
# The first 8 colors are the NEJM preset; the last 2 are generated.
```

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

Typical UI workflow:

1. Set `n`.
2. Choose a mode.
3. Apply a preset or roll a random palette.
4. Click any swatch to lock it.
5. Roll again to regenerate only unlocked swatches.
6. Double-click a swatch to type a HEX color manually.
7. Save the palette PNG or copy the Python array string.

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

See [REFERENCES.md](REFERENCES.md) for the algorithmic sources and how they map
to this implementation.

## License

Palette is released under the [MIT License](LICENSE).

MIT is a good fit for this project because it is a short permissive license that
allows use, modification, distribution, and commercial use while requiring the
copyright and license notice to be preserved.

## Development

```bash
python3 -m pip install -e ".[test]"
python3 -m pytest -q
python3 -m compileall -q src palette_ui.py
```

The project intentionally avoids image-generation dependencies for PNG export;
the UI writes simple PNG files with the Python standard library.
