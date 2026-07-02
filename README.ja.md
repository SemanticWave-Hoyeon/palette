# Paper Palette

[English](README.md) | [한국어](README.ko.md) | [简体中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md)

Paper Palette は、論文図表やデータ可視化に使いやすい配色を生成する
Python ライブラリ兼小さなデスクトップ UI です。OKLab/OKLCH などの知覚色空間を
使い、色覚特性にも配慮したパレットを作ることを目標にしています。

- `aesthetic`: UI、発表資料、デザイン向けのまとまりのあるパレット
- `categorical`: 論文図表やグループ比較向けの、互いに区別しやすいパレット

返り値は常に大文字の `#RRGGBB` 文字列です。ユーザーが指定した色を先頭に
固定し、残りの色だけを互換性のある色で補完できます。生成された色は
OKLCH hue で並び替えられるため、赤、橙、黄、緑、青、紫に近い流れで
見やすく表示されます。

## 例

**Aesthetic パレット**

![Aesthetic palette generated with seed 42](docs/assets/aesthetic_seed42.png)

```python
PaperPalette(mode="aesthetic", seed=42).generate(n=6)
```

**Categorical パレット**

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

**色覚特性を考慮した categorical パレット**

![Deuteranopia-aware categorical palette generated with seed 42](docs/assets/deuteranopia_seed42.png)

```python
PaperPalette(mode="categorical", colorblind="deuteranopia", seed=42).generate(n=6)
```

**Observable プリセット**

![Observable preset palette](docs/assets/preset_observable.png)

```python
from paper_palette import preset_colors

preset_colors("observable")
```

## 特長

- `mode="aesthetic"` で統一感のあるデザイン用パレットを生成します。
- `mode="categorical"` で図表やグループ比較に向いた区別しやすい色を生成します。
- ユーザー指定色を保持したまま、残りの色を補完できます。
- 生成色を OKLCH hue 順に並べ、視覚的に追いやすくします。
- protanopia、deuteranopia、tritanopia、achromatopsia の色覚オプションを提供します。
- categorical では色名の分離、グレースケールでの明度差、背景とのコントラストを考慮します。
- 論文図表で使いやすいプリセットを含みます。
- Tkinter ベースのデスクトップ UI を提供します。
- 追加の画像ライブラリなしで PNG を保存できます。

## インストール

まず GitHub からプロジェクトを取得します。

```bash
git clone https://github.com/SemanticWave-Hoyeon/paper-palette.git
cd paper-palette
```

仮想環境の利用を推奨します。

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell では次のように有効化します。

```powershell
.\.venv\Scripts\Activate.ps1
```

プロジェクトのルートでパッケージをインストールします。

```bash
python3 -m pip install -e .
```

これで `paper_palette` パッケージと `paper-palette-ui` コマンドが使えます。
依存関係を明示的に先に入れたい場合は、次のコマンドを使います。

```bash
python3 -m pip install -r requirements.txt
python3 -m pip install -e .
```

動作確認:

```bash
python3 - <<'PY'
from paper_palette import PaperPalette
print(PaperPalette(mode="categorical", seed=42).generate(n=5))
PY
```

デスクトップ UI を起動します。

```bash
paper-palette-ui
```

## ライブラリの使い方

基本の生成器を import します。

```python
from paper_palette import PaperPalette
```

統一感のあるデザイン用パレット:

```python
colors = PaperPalette(mode="aesthetic", seed=42).generate(n=5)
print(colors)
```

![Library usage aesthetic palette](docs/assets/usage_aesthetic_n5.png)

区別しやすい図表用パレット:

```python
colors = PaperPalette(mode="categorical", seed=42).generate(n=8)
print(colors)
```

![Library usage categorical palette](docs/assets/categorical_seed42.png)

色覚特性を考慮した categorical パレット:

```python
colors = PaperPalette(
    mode="categorical",
    colorblind="deuteranopia",
    seed=42,
).generate(n=6)
```

![Library usage deuteranopia-aware categorical palette](docs/assets/deuteranopia_seed42.png)

ユーザー指定色は返り値の先頭に保持されます。

```python
colors = PaperPalette(mode="aesthetic").generate(
    n=4,
    seed_colors=["#1E88E5"],
)
print(colors)
# ["#1E88E5", ...]
```

## モードの選び方

1つの視覚テーマとしてまとまった配色が必要なら `aesthetic` を使います。

```python
PaperPalette(mode="aesthetic").generate(n=6)
```

`aesthetic` の既定値は `harmony="stable"` です。類似色とトーン中心の
テンプレートを優先し、落ち着いたパレットを作ります。より広い色相関係が
必要な場合は、次のように指定できます。

```python
PaperPalette(mode="aesthetic", harmony="expressive").generate(n=6)
PaperPalette(mode="aesthetic", harmony="triadic").generate(n=6)
```

各色が別の群やカテゴリを表す場合は `categorical` を使います。

```python
PaperPalette(mode="categorical").generate(n=6)
```

## オプション

対応する `colorblind` 値:

- `None`
- `"protanopia"`
- `"deuteranopia"`
- `"tritanopia"`
- `"achromatopsia"`

対応する `background` 値:

- `"white"`
- `"black"`
- `"light"`
- `"dark"`

対応する `harmony` 値:

- `"stable"`
- `"expressive"`
- `"analogous"`
- `"monochrome_accent"`
- `"split_complementary"`
- `"triadic"`

`harmony` は `mode="aesthetic"` のときだけ意味があります。既定の
`stable` では split-complementary と triadic は使いません。小さな UI や
発表資料では散らばって見えやすいためです。より強い色相関係が必要な場合に
`expressive` またはテンプレート名を直接指定します。

## プリセット

論文図表向けの categorical プリセットを public API から使えます。

```python
from paper_palette import PaperPalette, list_presets, preset_colors

list_presets()
preset_colors("observable", n=5)
PaperPalette(mode="categorical").preset("nejm", n=10)
```

主なプリセット:

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

プリセットより大きい `n` を指定すると、プリセット色を先頭に保持し、
不足分を互換性のある色で生成します。

## API 参照

| API | 用途 |
| --- | --- |
| `PaperPalette(mode="aesthetic", seed=None, colorblind=None, background="white", harmony="stable")` | メイン生成器です。短い別名として `Palette` も使えます。 |
| `.generate(n, seed_colors=None)` | 大文字の `#RRGGBB` 文字列をちょうど `n` 個返します。 |
| `.preset(name, n=None, extend=True)` | 名前付きプリセットを返します。`n` がプリセットより大きく `extend=True` の場合、後ろに互換色を追加生成します。 |
| `list_presets()` | 利用可能なプリセット名を返します。 |
| `preset_colors(name, n=None)` | プリセット色を正規化された HEX 文字列で返します。 |

`seed` を指定すると結果を再現できます。入力色は `#RGB`, `#RRGGBB`,
`#RRGGBBAA` に対応し、出力は常に大文字の `#RRGGBB` です。不正な値は
`ValueError` になります。

## 比較と品質

![Matplotlib tab10 compared with Paper Palette categorical palettes](docs/assets/comparison_matplotlib.png)

Paper Palette は `colorspace` のような本格的な色彩科学パッケージを置き換える
ものではありません。論文図表向けの categorical パレット、プリセット拡張、
軽量な色固定 UI を小さな Python パッケージで使いやすくすることに焦点を置いています。

OKLab 距離、色覚シミュレーション後の距離、背景コントラスト、実行時間の測定値は
[docs/QUALITY.md](docs/QUALITY.md) にまとめています。

## デスクトップ UI

![Paper Palette desktop UI with the Observable preset applied](docs/assets/desktop_ui.png)

起動:

```bash
paper-palette-ui
```

ローカル開発中は次のランチャーも使えます。

```bash
python3 paper_palette_ui.py
python3 palette_ui.py
```

UI では、`n` の指定、プリセット適用、ランダム生成、背景指定、スウォッチの
ロック、HEX 色編集、PNG 保存、Python 配列文字列のコピーができます。

## アルゴリズム

Paper Palette は内部計算に OKLab/OKLCH を使います。RGB や HSV よりも、
人間が感じる明度、彩度、色相差に近い扱いをするためです。

`aesthetic` モードは候補パレットを多数作り、スコアリングして選びます。
既定では類似色とトーン中心の候補を使い、色相のまとまり、明度差、彩度バランス、
中立色とアクセント色の比率、重複回避、濁った色や過度に鮮やかな色への
ペナルティを考慮します。

`categorical` モードは、知覚色空間で既存色から遠い色を順に選ぶ
Glasbey 風の greedy farthest-point 戦略を使います。色名の分離、
グレースケール印刷での明度差、選択した `background` とのコントラストも
スコアに含めます。

## ライセンス

Paper Palette は [MIT License](LICENSE) で公開されています。

## 開発

```bash
python3 -m pip install -r requirements-dev.txt
python3 -m pip install -e .
python3 -m pytest -q
python3 -m compileall -q src paper_palette_ui.py palette_ui.py
```
