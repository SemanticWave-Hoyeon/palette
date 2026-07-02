# Paper Palette

[English README](README.md)

Paper Palette는 색상 팔레트를 만드는 Python 라이브러리이자 작은 데스크톱 UI입니다.
지각 색공간을 이용해 논문 그림에 바로 쓸 수 있고 색각 이상 조건도 고려한
팔레트를 만드는 것을 목표로 합니다.
용도는 크게 두 가지로 나뉩니다.

- `aesthetic`: UI, 발표 자료, 디자인 작업처럼 한 분위기로 묶이는 팔레트
- `categorical`: 논문 그림이나 차트처럼 항목끼리 잘 구분되는 팔레트

반환값은 항상 대문자 `#RRGGBB` 문자열입니다. 사용자가 지정한 색을 앞에
그대로 두고, 나머지 색만 어울리게 채울 수도 있습니다. 새로 생성한 색은
OKLCH hue 기준으로 정렬해 빨강, 주황, 노랑, 초록, 파랑, 보라에 가까운
흐름으로 보이게 합니다.

## 예시

**Aesthetic 팔레트**

![Aesthetic palette generated with seed 42](docs/assets/aesthetic_seed42.png)

```python
PaperPalette(mode="aesthetic", seed=42).generate(n=6)
```

**Categorical 팔레트**

![Categorical palette generated with seed 42](docs/assets/categorical_seed42.png)

```python
PaperPalette(mode="categorical", seed=42).generate(n=8)
```

**색각 이상 조건을 고려한 categorical 팔레트**

![Deuteranopia-aware categorical palette generated with seed 42](docs/assets/deuteranopia_seed42.png)

```python
PaperPalette(mode="categorical", colorblind="deuteranopia", seed=42).generate(n=6)
```

**Observable 프리셋**

![Observable preset palette](docs/assets/preset_observable.png)

```python
preset_colors("observable")
```

## 기능

- `mode="aesthetic"`으로 분위기가 맞는 디자인 팔레트를 생성합니다.
- `mode="categorical"`로 차트와 논문 그림에 쓰기 좋은 구분형 팔레트를 생성합니다.
- 사용자가 입력한 색을 고정한 채 나머지 색을 채울 수 있습니다.
- 새로 생성한 색을 OKLCH hue 순서로 정렬해 비슷한 색끼리 가깝게 배치합니다.
- 색각 이상 옵션을 지원합니다.
- categorical 색상을 고를 때 색 이름 계열, 흑백 명도 차이, 배경 대비를 함께 봅니다.
- 논문 그림에 자주 쓰이는 저널 스타일 프리셋을 제공합니다.
- Tkinter 기반 데스크톱 UI를 제공합니다.
- 별도 이미지 라이브러리 없이 팔레트 미리보기를 PNG로 저장합니다.

## 설치

먼저 GitHub에서 프로젝트를 내려받습니다.

```bash
git clone https://github.com/SemanticWave-Hoyeon/paper-palette.git
cd paper-palette
```

가상환경을 만들어 쓰는 것을 권장합니다.

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell에서는 다음처럼 활성화합니다.

```powershell
.\.venv\Scripts\Activate.ps1
```

프로젝트 루트에서 패키지를 설치합니다.

```bash
python3 -m pip install -e .
```

이 명령은 `paper_palette` 패키지와 `paper-palette-ui` 실행 명령을 설치합니다.
로컬에서 개발하거나 바로 수정해 가며 쓸 때는 editable 설치가 편합니다.

설치가 잘 됐는지 간단히 확인합니다.

```bash
python3 - <<'PY'
from paper_palette import PaperPalette
print(PaperPalette(mode="categorical", seed=42).generate(n=5))
PY
```

데스크톱 UI는 다음 명령으로 실행합니다.

```bash
paper-palette-ui
```

테스트까지 실행하려면 다음처럼 설치합니다.

```bash
python3 -m pip install -e ".[test]"
python3 -m pytest -q
```

## 라이브러리 사용법

먼저 `PaperPalette`를 불러옵니다.

```python
from paper_palette import PaperPalette
```

디자인용 팔레트를 만들 때는 `aesthetic` 모드를 씁니다.

```python
colors = PaperPalette(mode="aesthetic", seed=42).generate(n=5)
print(colors)
```

논문 그래프나 차트처럼 색을 서로 확실히 구분해야 할 때는 `categorical`
모드를 씁니다.

```python
colors = PaperPalette(mode="categorical", seed=42).generate(n=8)
print(colors)
```

색각 이상 조건을 고려할 수도 있습니다.

```python
colors = PaperPalette(
    mode="categorical",
    colorblind="deuteranopia",
    seed=42,
).generate(n=6)
```

어두운 배경의 차트에 쓸 팔레트도 만들 수 있습니다.

```python
colors = PaperPalette(
    mode="categorical",
    background="dark",
    seed=42,
).generate(n=7)
```

이미 정해 둔 색이 있으면 `seed_colors`로 넘깁니다. 입력한 색은 반환된
팔레트 앞쪽에 그대로 유지됩니다.

```python
colors = PaperPalette(mode="aesthetic").generate(
    n=4,
    seed_colors=["#1E88E5"],
)
print(colors)
# ["#1E88E5", ...]
```

이미 정한 원고 색이나 브랜드 색을 잠근 채 나머지 색을 채울 수도 있습니다.

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

접근성을 고려한 Petroff color cycle 프리셋도 바로 쓸 수 있습니다.

```python
from paper_palette import preset_colors

colors = preset_colors("accessible8")
```

지원하는 `mode` 값은 다음과 같습니다.

- `aesthetic`: UI, 발표 자료, 디자인처럼 한 시각적 분위기가 필요한 경우
- `categorical`: 차트, 논문 그림, 그룹 비교처럼 색을 구분해야 하는 경우

지원하는 `colorblind` 값은 다음과 같습니다.

- `None`
- `"protanopia"`
- `"deuteranopia"`
- `"tritanopia"`
- `"achromatopsia"`

지원하는 `background` 값은 다음과 같습니다.

- `"white"`
- `"black"`
- `"light"`
- `"dark"`

색상 입력은 `#RGB`, `#RRGGBB`, `#RRGGBBAA` 형식을 받습니다. 출력은 항상
대문자 `#RRGGBB`로 정규화됩니다. 잘못된 입력은 `ValueError`를 발생시킵니다.

## 어떤 모드를 써야 하나요?

비슷한 계열의 색으로 화면이나 문서의 분위기를 맞추고 싶다면 `aesthetic`을
쓰면 됩니다.

```python
PaperPalette(mode="aesthetic").generate(n=6)
```

실험군, 모델, 카테고리처럼 각각의 색이 명확히 달라야 한다면
`categorical`이 더 맞습니다.

```python
PaperPalette(mode="categorical").generate(n=6)
```

## 프리셋

논문 그림에 쓰기 좋은 categorical 프리셋을 함께 제공합니다.

```python
from paper_palette import PaperPalette, list_presets, preset_colors

list_presets()
preset_colors("observable", n=5)
PaperPalette(mode="categorical").preset("nejm", n=10)
```

포함된 프리셋은 다음과 같습니다.

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

일부 프리셋 원본은 `#RRGGBBAA` 형식이지만, Paper Palette는 이를 `#RRGGBB`로
정규화합니다. `n`이 프리셋 색상 수보다 크면 프리셋 색을 먼저 두고,
부족한 색은 알고리즘으로 추가 생성합니다.

```python
palette = PaperPalette(mode="categorical", seed=7).preset("nejm", n=10)
print(palette)
# 앞의 8개는 NEJM 프리셋이고, 뒤의 2개는 새로 생성된 색입니다.
```

## API 요약

| API | 용도 |
| --- | --- |
| `PaperPalette(mode="aesthetic", seed=None, colorblind=None, background="white")` | 기본 생성기입니다. 짧은 이름인 `Palette`도 함께 제공합니다. |
| `.generate(n, seed_colors=None)` | 정확히 `n`개의 색을 대문자 `#RRGGBB` 문자열로 반환합니다. |
| `.preset(name, n=None, extend=True)` | 이름이 있는 프리셋을 반환합니다. `n`이 프리셋보다 크고 `extend=True`이면 부족한 색을 뒤에 생성합니다. |
| `list_presets()` | 사용할 수 있는 프리셋 이름을 반환합니다. |
| `preset_colors(name, n=None)` | 프리셋 색을 정규화된 HEX 문자열로 반환합니다. |

`seed`를 지정하면 같은 결과를 다시 만들 수 있습니다. `seed_colors`로 넘긴
색은 결과 앞쪽에 유지되고, 그 뒤에 새로 생성된 색은 지각적 hue 순서로
정렬됩니다. 잘못된 색상이나 잘못된 개수는 `ValueError`를 발생시킵니다.

## 비교 예시

아래 이미지는 흔히 쓰는 Matplotlib categorical 팔레트와 Paper Palette의
categorical 결과, 색각 이상 조건을 고려한 결과, Petroff accessible color cycle
프리셋을 비교한 것입니다. Deuteranopia 시뮬레이션과 흑백 스트립도 함께 넣어
구분성을 더 쉽게 확인할 수 있게 했습니다.

![Matplotlib tab10 compared with Paper Palette categorical palettes](docs/assets/comparison_matplotlib.png)

Paper Palette는 `colorspace` 같은 본격적인 색채 과학 패키지를 대체하려는
도구는 아닙니다. 작은 Python 패키지 안에서 논문 그림용 categorical 팔레트,
프리셋 확장, 색상 고정 UI를 쉽게 쓰는 데 초점을 둡니다.

## 데스크톱 UI

![Paper Palette desktop UI with the Observable preset applied](docs/assets/desktop_ui.png)

설치 후 다음 명령으로 실행합니다.

```bash
paper-palette-ui
```

로컬 개발 중에는 런처 파일을 바로 실행해도 됩니다.

```bash
python3 paper_palette_ui.py
```

UI에서 할 수 있는 일은 다음과 같습니다.

- `n` 값을 지정해 색상 개수를 정합니다.
- 프리셋을 적용합니다.
- 주사위 버튼으로 새 팔레트를 생성합니다.
- 흰색, 밝은색, 검은색, 어두운색 배경을 고릅니다.
- 색상 사각형을 클릭해 고정하거나 해제합니다.
- 색상 사각형을 더블클릭해 HEX 코드를 직접 입력합니다.
- 팔레트를 `outputs/` 폴더에 PNG로 저장합니다.
- 현재 팔레트를 Python 배열 문자열로 복사합니다.

프리셋을 적용하면 프리셋 색상은 자동으로 고정됩니다. `n`이 프리셋보다
크면 원래 프리셋 색상만 고정되고, 추가 생성된 색은 고정되지 않습니다.
잠긴 색이 없을 때 주사위 버튼을 누르면 전체 팔레트가 hue 순서로 보입니다.
일부 색이 잠겨 있으면 잠긴 위치는 유지하고, 새로 생성되는 색들만 hue 순서로
채웁니다.

일반적인 사용 흐름은 다음과 같습니다.

1. `n` 값을 정합니다.
2. 모드를 고릅니다.
3. 프리셋을 적용하거나 주사위 버튼을 누릅니다.
4. 유지할 색상은 클릭해서 고정합니다.
5. 다시 주사위 버튼을 눌러 고정되지 않은 색만 바꿉니다.
6. 필요한 색은 더블클릭해서 직접 입력합니다.
7. PNG로 저장하거나 Python 배열 문자열로 복사합니다.

## 알고리즘

Paper Palette는 내부 계산에 OKLab/OKLCH를 사용합니다. RGB나 HSV보다 명도,
채도, 색상 차이를 사람이 느끼는 방식에 가깝게 다루기 위해서입니다.

`aesthetic` 모드는 여러 후보 팔레트를 만든 뒤 점수화해 고르는 방식입니다.
유사색과 톤 중심의 후보를 만들고, 색상 응집도, 명도 대비, 채도 균형,
중립색과 포인트 색의 비율, 중복 색 회피, 탁하거나 지나치게 튀는 색에 대한
패널티를 함께 봅니다.

`categorical` 모드는 Glasbey 방식과 비슷한 greedy farthest-point 전략을
사용합니다. 이미 고른 색들과 지각적으로 멀리 떨어진 색을 차례로 고릅니다.
여기에 Colorgorical 계열 연구에서 쓰는 색 이름 차이 개념, 흑백 출력에 필요한
명도 차이, 선택한 `background`와의 대비를 점수에 함께 넣습니다. Greedy 선택이
끝난 뒤에는 짧은 local refinement 단계에서 후보 교체를 시도하고, 전체 팔레트
점수가 좋아지는 경우만 반영합니다.

생성이 끝난 뒤에는 새로 생성된 색을 OKLCH hue 기준으로 정렬합니다. 색을 다시
고르는 것이 아니라, 선택된 색의 순서만 따뜻한 색에서 초록, 파랑, 보라 쪽으로
읽히게 바꿉니다. 사용자가 입력한 seed 색과 프리셋 색의 위치는 그대로 유지됩니다.

색각 이상 옵션을 켜면 protanopia, deuteranopia, tritanopia, achromatopsia
조건에서 보이는 색을 근사한 뒤, 그 상태에서도 색들이 충분히 구분되는지
확인합니다.

알고리즘 출처와 구현에 반영한 방식은 [REFERENCES.md](REFERENCES.md)에
정리해 두었습니다.

## 라이선스

Paper Palette는 [MIT License](LICENSE)로 배포됩니다.

MIT 라이선스는 이 프로젝트에 잘 맞습니다. 짧고 permissive한 라이선스라
사용, 수정, 배포, 상업적 사용을 폭넓게 허용하면서 저작권과 라이선스 고지만
유지하도록 요구합니다.

## 개발

```bash
python3 -m pip install -e ".[test]"
python3 -m pytest -q
python3 -m compileall -q src paper_palette_ui.py
```

PNG 내보내기는 별도 이미지 생성 라이브러리에 의존하지 않습니다. UI는 Python
표준 라이브러리만으로 간단한 PNG 파일을 씁니다.
