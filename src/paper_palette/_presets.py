from __future__ import annotations

from dataclasses import dataclass

from ._color import normalize_hex


@dataclass(frozen=True)
class Preset:
    name: str
    label: str
    colors: tuple[str, ...]
    aliases: tuple[str, ...] = ()


_PRESET_DATA = {
    "npg": Preset(
        name="npg",
        label="Nature Publishing Group",
        colors=(
            "#E64B35",
            "#4DBBD5",
            "#00A087",
            "#3C5488",
            "#F39B7F",
            "#8491B4",
            "#91D1C2",
            "#DC0000",
            "#7E6148",
            "#B09C85",
        ),
        aliases=("nature", "npg10"),
    ),
    "observable": Preset(
        name="observable",
        label="Observable 10",
        colors=(
            "#4269D0",
            "#EFB118",
            "#FF725C",
            "#6CC5B0",
            "#3CA951",
            "#FF8AB7",
            "#A463F2",
            "#97BBF5",
            "#9C6B4E",
            "#9498A0",
        ),
        aliases=("obs", "observable10"),
    ),
    "bmj": Preset(
        name="bmj",
        label="BMJ",
        colors=(
            "#2A6EBB",
            "#F0AB00",
            "#C50084",
            "#7D5CC6",
            "#E37222",
            "#69BE28",
            "#00B2A9",
            "#CD202C",
            "#747678",
        ),
        aliases=("bmj9",),
    ),
    "science": Preset(
        name="science",
        label="Science / AAAS",
        colors=(
            "#3B4992",
            "#EE0000",
            "#008B45",
            "#631879",
            "#008280",
            "#BB0021",
            "#5F559B",
            "#A20056",
            "#808180",
            "#1B1919",
        ),
        aliases=("aaas", "science10"),
    ),
    "nejm": Preset(
        name="nejm",
        label="NEJM",
        colors=(
            "#BC3C29",
            "#0072B5",
            "#E18727",
            "#20854E",
            "#7876B1",
            "#6F99AD",
            "#FFDC91",
            "#EE4C97",
        ),
        aliases=("nejm8",),
    ),
    "lancet": Preset(
        name="lancet",
        label="Lancet",
        colors=(
            "#00468B",
            "#ED0000",
            "#42B540",
            "#0099B4",
            "#925E9F",
            "#FDAF91",
            "#AD002A",
            "#ADB6B6",
            "#1B1919",
        ),
        aliases=("lancet10",),
    ),
    "jco": Preset(
        name="jco",
        label="Journal of Clinical Oncology",
        colors=(
            "#0073C2",
            "#EFC000",
            "#868686",
            "#CD534C",
            "#7AA6DC",
            "#003C67",
            "#8F7700",
            "#3B3B3B",
            "#A73030",
        ),
        aliases=("clinical oncology", "oncology", "jco10"),
    ),
    "petroff6": Preset(
        name="petroff6",
        label="Petroff Accessible 6",
        colors=(
            "#5790FC",
            "#F89C20",
            "#E42536",
            "#964A8B",
            "#9C9CA1",
            "#7A21DD",
        ),
        aliases=("accessible6", "accessible color cycle 6"),
    ),
    "petroff8": Preset(
        name="petroff8",
        label="Petroff Accessible 8",
        colors=(
            "#1845FB",
            "#FF5E02",
            "#C91F16",
            "#C849A9",
            "#ADAD7D",
            "#86C8DD",
            "#578DFF",
            "#656364",
        ),
        aliases=("accessible8", "accessible color cycle 8"),
    ),
    "petroff10": Preset(
        name="petroff10",
        label="Petroff Accessible 10",
        colors=(
            "#3F90DA",
            "#FFA90E",
            "#BD1F01",
            "#94A4A2",
            "#832DB6",
            "#A96B59",
            "#E76300",
            "#B9AC70",
            "#717581",
            "#92DADD",
        ),
        aliases=("accessible", "accessible10", "accessible color cycle 10", "petroff"),
    ),
}

_ALIASES = {
    alias.lower(): name
    for name, preset in _PRESET_DATA.items()
    for alias in (name, *preset.aliases)
}


def list_presets() -> list[str]:
    return list(_PRESET_DATA)


def preset_label(name: str) -> str:
    return _preset(name).label


def preset_colors(name: str, n: int | None = None) -> list[str]:
    preset = _preset(name)
    colors = [normalize_hex(color) for color in preset.colors]
    if n is None:
        return colors
    if not isinstance(n, int):
        raise ValueError("n must be an integer.")
    if n <= 0:
        raise ValueError("n must be greater than 0.")
    return colors[:n]


def preset_size(name: str) -> int:
    return len(_preset(name).colors)


def _preset(name: str) -> Preset:
    if not isinstance(name, str):
        raise ValueError("Preset name must be a string.")
    key = _ALIASES.get(name.strip().lower())
    if key is None:
        available = ", ".join(list_presets())
        raise ValueError(f"Unknown preset {name!r}. Available presets: {available}.")
    return _PRESET_DATA[key]
