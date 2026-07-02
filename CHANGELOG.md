# Changelog

## v1.1.0 - 2026-07-02

- Add `harmony` control for aesthetic palettes.
- Keep `harmony="stable"` as the default, while allowing `expressive`,
  `analogous`, `monochrome_accent`, `split_complementary`, and `triadic`.
- Document why split-complementary and triadic templates are disabled in the
  default stable mix.
- Add a quality and performance report with OKLab separation, colorblind
  simulation separation, background contrast, and runtime measurements.
- Add a reproducible benchmark script for future comparisons.

## v1.0.0 - 2026-07-02

First stable release.

- Finalize the public `paper_palette` package API with `Palette`,
  `PaperPalette`, presets, colorblind-aware generation, and PNG export support.
- Polish the Tkinter desktop UI with grouped controls, a fixed-size layout,
  larger swatches, a status bar, fixed-seed controls, and a canvas color picker.
- Add README and Korean README installation guides, generated palette examples,
  Matplotlib chart examples, and desktop UI screenshots.
- Document algorithm and preset references.
- Keep the project on MIT license with tests and GitHub Actions CI.

## v0.2.2 - 2026-07-02

- Add incremental minimum-distance caches for aesthetic and categorical greedy
  selection, reducing repeated pool-to-selection scans.
- Preserve generated OKLCH candidates through gamut filtering to avoid
  RGB-to-OKLab-to-OKLCH round trips during candidate pool construction.
- Remove repeated `vstack` accumulation from selection loops.
- Reuse pool metadata during categorical refinement.

## v0.2.1 - 2026-07-02

- Optimize palette generation by removing redundant selected-color conversions
  and repeated distance calculations.
- Avoid storing and computing simulated color-vision arrays when colorblind
  mode is disabled.
- Precompute categorical pool scores that do not change across selection steps.
- Reduce temporary memory in pairwise distance calculations.

## v0.2.0 - 2026-07-02

- Sort newly generated colors by OKLCH hue so random palettes display in a
  warm-to-cool visual order.
- Preserve seed and preset positions while sorting only generated additions.
- Improve `categorical` generation with color-name separation, grayscale
  lightness separation, background-aware scoring, and local refinement.
- Add `background` support to the library and desktop UI.
- Add Petroff accessible color-cycle presets.
- Add stronger README examples and a clearer comparison figure.

## v0.1.0 - 2026-07-02

Initial public release.

- Add `paper_palette` package with `PaperPalette` and `Palette` APIs.
- Add aesthetic and categorical palette generation modes.
- Add seed color extension and journal-style presets.
- Add colorblind-aware generation options.
- Add Tkinter desktop UI with locking, HEX editing, PNG export, and copy support.
- Add README examples, Korean README, references, tests, and CI.
