# Changelog

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
