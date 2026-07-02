# Paper Palette

[English](README.md) | [한국어](README.ko.md) | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

Paper Palette 是一个用于生成颜色调色板的 Python 库，同时提供一个轻量级桌面 UI。
它面向论文图表、数据可视化和演示材料，使用 OKLab/OKLCH 等感知色彩空间，
并支持色觉障碍条件下的配色检查。

- `aesthetic`：适合 UI、演示和设计的统一风格调色板
- `categorical`：适合论文图表、分组数据和类别比较的高区分度调色板

库始终返回大写 `#RRGGBB` 字符串。你可以把用户指定的颜色固定在结果前面，
再让算法补全剩余颜色。新生成的颜色会按 OKLCH hue 排序，因此相邻色块通常会
呈现接近红、橙、黄、绿、蓝、紫的视觉顺序。

## 示例

**Aesthetic 调色板**

![Aesthetic palette generated with seed 42](docs/assets/aesthetic_seed42.png)

```python
PaperPalette(mode="aesthetic", seed=42).generate(n=6)
```

**Categorical 调色板**

![Categorical palette generated with seed 42](docs/assets/categorical_seed42.png)

```python
PaperPalette(mode="categorical", seed=42).generate(n=8)
```

**Matplotlib categorical 图表示例**

![Matplotlib pie, line, bar, and box plot examples using Paper Palette categorical colors](docs/assets/matplotlib_chart_examples.png)

```python
import matplotlib.pyplot as plt
from paper_palette import PaperPalette

colors = PaperPalette(mode="categorical", seed=73).generate(n=8)

plt.pie([24, 18, 21, 14, 23], colors=colors[:5])
plt.show()
```

**考虑色觉障碍的 categorical 调色板**

![Deuteranopia-aware categorical palette generated with seed 42](docs/assets/deuteranopia_seed42.png)

```python
PaperPalette(mode="categorical", colorblind="deuteranopia", seed=42).generate(n=6)
```

**Observable 预设**

![Observable preset palette](docs/assets/preset_observable.png)

```python
from paper_palette import preset_colors

preset_colors("observable")
```

## 功能

- 使用 `mode="aesthetic"` 生成风格统一的设计调色板。
- 使用 `mode="categorical"` 生成适合图表和分组数据的高区分度调色板。
- 可以保留用户输入的颜色，只补全剩余颜色。
- 按 OKLCH hue 对新生成的颜色排序，便于视觉浏览。
- 支持 protanopia、deuteranopia、tritanopia、achromatopsia。
- categorical 模式会考虑颜色名称分离、灰度/明度分离以及白色或深色背景对比。
- 内置适合论文图表的期刊风格预设。
- 提供 Tkinter 桌面 UI。
- 不依赖额外图像库即可保存 PNG 预览。

## 安装

先从 GitHub 下载项目：

```bash
git clone https://github.com/SemanticWave-Hoyeon/paper-palette.git
cd paper-palette
```

建议使用虚拟环境：

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell：

```powershell
.\.venv\Scripts\Activate.ps1
```

在项目根目录安装：

```bash
python3 -m pip install -e .
```

这会安装 `paper_palette` 包和 `paper-palette-ui` 命令。如果想先显式安装依赖：

```bash
python3 -m pip install -r requirements.txt
python3 -m pip install -e .
```

检查库是否可用：

```bash
python3 - <<'PY'
from paper_palette import PaperPalette
print(PaperPalette(mode="categorical", seed=42).generate(n=5))
PY
```

启动桌面 UI：

```bash
paper-palette-ui
```

开发时安装测试依赖：

```bash
python3 -m pip install -r requirements-dev.txt
python3 -m pip install -e .
python3 -m pytest -q
```

## 库用法

导入主生成器：

```python
from paper_palette import PaperPalette
```

生成风格统一的设计调色板：

```python
colors = PaperPalette(mode="aesthetic", seed=42).generate(n=5)
print(colors)
```

![Library usage aesthetic palette](docs/assets/usage_aesthetic_n5.png)

生成高区分度图表调色板：

```python
colors = PaperPalette(mode="categorical", seed=42).generate(n=8)
print(colors)
```

![Library usage categorical palette](docs/assets/categorical_seed42.png)

生成考虑色觉障碍的 categorical 调色板：

```python
colors = PaperPalette(
    mode="categorical",
    colorblind="deuteranopia",
    seed=42,
).generate(n=6)
```

![Library usage deuteranopia-aware categorical palette](docs/assets/deuteranopia_seed42.png)

为深色图表背景生成调色板：

```python
colors = PaperPalette(
    mode="categorical",
    background="dark",
    seed=42,
).generate(n=7)
```

![Library usage dark-background categorical palette](docs/assets/usage_categorical_dark_seed42.png)

用户指定的颜色会保留在返回结果前面：

```python
colors = PaperPalette(mode="aesthetic").generate(
    n=4,
    seed_colors=["#1E88E5"],
)
print(colors)
# ["#1E88E5", ...]
```

![Library usage aesthetic palette with a preserved seed color](docs/assets/usage_seed_color_aesthetic.png)

## 如何选择模式

如果希望配色像一个统一主题，请使用 `aesthetic`：

```python
PaperPalette(mode="aesthetic").generate(n=6)
```

`aesthetic` 的默认值是 `harmony="stable"`。它会优先使用类似色和同一色调家族，
生成更稳、更统一的调色板。如果希望在仍然协调的前提下增加色相跨度，可以这样写：

```python
PaperPalette(mode="aesthetic", harmony="expressive").generate(n=6)
PaperPalette(mode="aesthetic", harmony="triadic").generate(n=6)
```

如果每种颜色代表不同类别、模型或实验组，请使用 `categorical`：

```python
PaperPalette(mode="categorical").generate(n=6)
```

## 支持的选项

`colorblind`：

- `None`
- `"protanopia"`
- `"deuteranopia"`
- `"tritanopia"`
- `"achromatopsia"`

`background`：

- `"white"`
- `"black"`
- `"light"`
- `"dark"`

`harmony`，仅对 `mode="aesthetic"` 有意义：

- `"stable"`
- `"expressive"`
- `"analogous"`
- `"monochrome_accent"`
- `"split_complementary"`
- `"triadic"`

默认 `stable` 不启用 split-complementary 和 triadic 模板，因为它们在小型 UI 或
演示用调色板中可能显得不够统一。需要更强的色相关系时，可以使用
`expressive` 或直接指定模板名。

## 预设

可以通过 public API 使用论文图表风格的 categorical 预设：

```python
from paper_palette import PaperPalette, list_presets, preset_colors

list_presets()
preset_colors("observable", n=5)
PaperPalette(mode="categorical").preset("nejm", n=10)
```

包含的预设：

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

如果 `n` 大于预设颜色数量，Paper Palette 会先保留预设颜色，再生成兼容的补充颜色。

## API 参考

| API | 用途 |
| --- | --- |
| `PaperPalette(mode="aesthetic", seed=None, colorblind=None, background="white", harmony="stable")` | 主生成器。`Palette` 是较短的别名。 |
| `.generate(n, seed_colors=None)` | 返回正好 `n` 个大写 `#RRGGBB` 字符串。 |
| `.preset(name, n=None, extend=True)` | 返回命名预设。如果 `n` 大于预设并且 `extend=True`，会在后面生成兼容颜色。 |
| `list_presets()` | 返回可用预设名称。 |
| `preset_colors(name, n=None)` | 返回规范化后的预设 HEX 字符串。 |

`seed` 用于复现结果。`seed_colors` 会保留在结果前面，新生成的颜色会按感知 hue
排序。颜色输入支持 `#RGB`、`#RRGGBB`、`#RRGGBBAA`，输出始终规范化为大写
`#RRGGBB`。无效输入会抛出 `ValueError`。

## 比较与质量

![Matplotlib tab10 compared with Paper Palette categorical palettes](docs/assets/comparison_matplotlib.png)

Paper Palette 并不是为了取代 `colorspace` 这类完整色彩科学库。它的重点是：
在一个小型 Python 包里方便地生成论文图表用 categorical 调色板、扩展预设、
并通过轻量桌面 UI 固定颜色。

OKLab 距离、色觉模拟后的距离、背景对比和运行时间测量见
[docs/QUALITY.md](docs/QUALITY.md)。

## 桌面 UI

![Paper Palette desktop UI with the Observable preset applied](docs/assets/desktop_ui.png)

运行：

```bash
paper-palette-ui
```

本地开发时也可以运行：

```bash
python3 paper_palette_ui.py
python3 palette_ui.py
```

UI 支持设置 `n`、应用预设、随机生成、选择背景、锁定色块、双击编辑 HEX 颜色、
保存 PNG 到 `outputs/`，以及把当前调色板复制为 Python 数组字符串。

## 算法

Paper Palette 内部使用 OKLab/OKLCH，使距离和协调性评分比 RGB 或 HSV 更接近
人类感知。

`aesthetic` 模式会生成许多候选调色板，再按整体分数选择。默认使用类似色和同一色调
家族，并同时考虑 hue 一致性、明度对比、彩度平衡、中性色/强调色比例、避免重复、
以及对浑浊或过度鲜艳颜色的惩罚。

`categorical` 模式使用类似 Glasbey 的 greedy farthest-point 策略，在感知色彩空间中
依次选择距离已有颜色尽量远的新颜色。评分中还包括颜色名称分离、灰度打印时的明度差、
以及与所选 `background` 的对比。

## 许可证

Paper Palette 使用 [MIT License](LICENSE) 发布。

## 开发

```bash
python3 -m pip install -r requirements-dev.txt
python3 -m pip install -e .
python3 -m pytest -q
python3 -m compileall -q src paper_palette_ui.py palette_ui.py
```
