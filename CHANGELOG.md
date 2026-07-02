# Changelog

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
