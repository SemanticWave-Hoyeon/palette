# References

Paper Palette is an original implementation, but the design follows established work
in perceptual color spaces, color harmony, categorical palette construction,
and color vision deficiency simulation.

## Perceptual Color Space

- Bjorn Ottosson, "A perceptual color space for image processing"  
  https://bottosson.github.io/posts/oklab/

Paper Palette uses OKLab and OKLCH internally for color conversion, candidate
sampling, perceptual distance scoring, and hue/lightness/chroma-based
constraints. The implementation does not copy code from Ottosson's article; it
implements the published conversion equations.

## Aesthetic Palette Scoring

- Peter O'Donovan, Aseem Agarwala, and Aaron Hertzmann, "Color Compatibility
  From Large Datasets," ACM Transactions on Graphics, 2011  
  https://www.dgp.toronto.edu/~donovan/color/

- Daniel Cohen-Or, Olga Sorkine, Ran Gal, Tommer Leyvand, and Ying-Qing Xu,
  "Color Harmonization," ACM Transactions on Graphics, 2006  
  https://igl.ethz.ch/projects/color-harmonization/harmonization.pdf

Paper Palette's `aesthetic` mode is inspired by this line of work. Instead of
using a single hue rotation formula, it samples many candidate palettes and
scores the whole palette for hue cohesion, lightness contrast, chroma balance,
neutral/accent balance, duplicate avoidance, and muddy/neon penalties.

## Categorical Palette Generation

- Chris A. Glasbey, Gerie W. A. M. van der Heijden, Vivian F. K. Toh, and
  Alison Gray, "Colour Displays for Categorical Images," Colour Research &
  Application, 2007  
  https://pureportal.strath.ac.uk/en/publications/colour-displays-for-categorical-images

- Connor C. Gramazio, David H. Laidlaw, and Karen B. Schloss, "Colorgorical:
  Creating discriminable and preferable color palettes for information
  visualization," IEEE Transactions on Visualization and Computer Graphics,
  2017  
  https://doi.org/10.1109/TVCG.2016.2598918

- Matthew A. Petroff, "Accessible Color Sequences for Data Visualization,"
  2021  
  https://arxiv.org/abs/2107.02270

Paper Palette's `categorical` mode uses a Glasbey-style greedy farthest-point
selection strategy in perceptual color space: each added color is selected to
remain visually distinct from the colors already chosen. Version 0.2 adds
Colorgorical-inspired color-name separation, grayscale/lightness separation,
background contrast scoring, and a small local refinement pass over the greedy
result. Petroff's work informs the accessibility-oriented constraints and the
included accessible color-cycle presets.

## Colorblind-Aware Generation

- Gustavo M. Machado, Manuel M. Oliveira, and Leandro A. F. Fernandes, "A
  Physiologically-based Model for Simulation of Color Vision Deficiency," IEEE
  Transactions on Visualization and Computer Graphics, 2009  
  https://www.inf.ufrgs.br/~oliveira/pubs_files/CVD_Simulation/CVD_Simulation.html

- ColorBrewer 2.0, color advice for cartography  
  https://colorbrewer2.org/

Paper Palette simulates protanopia, deuteranopia, and tritanopia with
Machado-style matrices and uses the simulated colors as a distance constraint.
The ColorBrewer reference informs the practical UI/API idea that palettes used
for charts should offer colorblind-aware options.

## Presets

- Nan Xiao, "ggsci: Scientific Journal and Sci-Fi Themed Color Palettes for
  ggplot2"  
  https://github.com/nanxstats/ggsci

- ggsci documentation  
  https://nanx.me/ggsci/

- Matthew A. Petroff, "accessible-color-cycles"  
  https://github.com/mpetroff/accessible-color-cycles

The bundled journal-style presets follow the same broad family of scientific
figure palettes popularized by packages such as `ggsci`: NPG, AAAS/Science,
NEJM, Lancet, JCO, BMJ, and Observable-style categorical colors. The bundled
`petroff6`, `petroff8`, and `petroff10` presets follow the final accessible
color-cycle results published with Petroff's repository.

The preset names are descriptive labels for familiar palette styles. They do
not imply endorsement by, affiliation with, or trademark permission from the
named journals or organizations. Users should check publisher or brand
guidelines before using a palette in official materials.

Presets that originated in `#RRGGBBAA` form are normalized to `#RRGGBB` because
Paper Palette's public API returns opaque HEX colors.

## Comparison Baseline

- Matplotlib default color cycle / Tableau 10 colors  
  https://matplotlib.org/stable/users/explain/colors/colors.html

The README comparison image uses Matplotlib's common `tab10` categorical colors
as a familiar baseline, then shows Paper Palette's categorical and
colorblind-aware categorical outputs for the same number of colors.
