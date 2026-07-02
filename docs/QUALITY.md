# Quality and Performance Notes

This project uses research-informed heuristics rather than a formal guarantee of
publication quality. The numbers below make the current behavior easier to audit
and compare over time.

Run the report locally:

```bash
PYTHONPATH=src python3 benchmarks/evaluate_generation.py
```

Measured on macOS 26.5.1 with Python 3.14.5. Runtime values will vary by
machine.

## Categorical OKLab Separation and Runtime

The table reports the minimum pairwise OKLab distance for categorical palettes
generated with seeds 0-11. Larger values mean the closest pair in each palette is
farther apart in a perceptual color space.

| n | mean min OKLab distance | worst min OKLab distance | mean runtime ms | p95 runtime ms |
| --- | ---: | ---: | ---: | ---: |
| 3 | 0.3784 | 0.3633 | 10.9 | 18.8 |
| 5 | 0.2866 | 0.2169 | 29.5 | 58.8 |
| 8 | 0.2088 | 0.1688 | 60.3 | 63.6 |
| 10 | 0.1784 | 0.1632 | 72.2 | 101.3 |
| 20 | 0.1237 | 0.1155 | 172.7 | 183.1 |

## Colorblind Simulated Separation

The table reports minimum pairwise OKLab distances after Machado-style color
vision deficiency simulation for n=8 palettes generated with seeds 0-11.

| mode | n | mean min simulated OKLab distance | worst min simulated OKLab distance |
| --- | ---: | ---: | ---: |
| protanopia | 8 | 0.1173 | 0.0927 |
| deuteranopia | 8 | 0.1034 | 0.0746 |
| tritanopia | 8 | 0.1062 | 0.0791 |
| achromatopsia | 8 | 0.0232 | 0.0023 |

Achromatopsia collapses hue information into grayscale, so separation is much
harder than in the other simulated modes. For achromatopsia-heavy use cases,
prefer fewer categories, larger marks, labels, direct annotations, or distinct
line styles and markers.

## Background Contrast

The table reports the minimum WCAG-style contrast ratio between generated colors
and the target background. These values are useful for chart fills and strokes,
but they should not be read as a guarantee that white or black text placed on
each color will meet text accessibility thresholds.

| target background | n | mean minimum contrast ratio | worst minimum contrast ratio |
| --- | ---: | ---: | ---: |
| white | 8 | 1.73 | 1.64 |
| black | 8 | 2.87 | 2.66 |

## Recommended Use Range

- Best-tested range: 2-12 colors.
- Supported range in the desktop UI: 1-24 colors.
- Larger categorical palettes are possible, but the closest colors necessarily
  become less separated as n grows.
- For dense scientific figures, pair colors with labels, marker shapes, line
  styles, or direct annotations.
