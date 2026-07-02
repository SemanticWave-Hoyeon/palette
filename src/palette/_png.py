from __future__ import annotations

import struct
import zlib
from pathlib import Path

from ._color import normalize_hex

RGB = tuple[int, int, int]

_FONT_5X7 = {
    "#": ("01010", "11111", "01010", "01010", "11111", "01010", "00000"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "10000", "11110", "00001", "00001", "11110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01111", "10000", "10000", "10000", "10000", "10000", "01111"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
}


def save_palette_png(
    colors: list[str],
    path: str | Path,
    swatch_width: int = 180,
    swatch_height: int = 120,
    label_height: int = 42,
    padding: int = 18,
) -> Path:
    if not colors:
        raise ValueError("Cannot save an empty palette.")

    normalized = [normalize_hex(color) for color in colors]
    width = padding * 2 + swatch_width * len(normalized)
    height = padding * 2 + swatch_height + label_height
    pixels = bytearray([255] * (width * height * 3))

    for index, color in enumerate(normalized):
        x0 = padding + index * swatch_width
        y0 = padding
        _fill_rect(pixels, width, x0, y0, swatch_width, swatch_height, _hex_to_rgb(color))
        _draw_text_centered(
            pixels,
            width,
            x0,
            y0 + swatch_height + 13,
            swatch_width,
            color,
            scale=3,
            color=(20, 20, 20),
        )

    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    _write_png(output, width, height, bytes(pixels))
    return output


def _hex_to_rgb(color: str) -> RGB:
    normalized = normalize_hex(color)
    return (
        int(normalized[1:3], 16),
        int(normalized[3:5], 16),
        int(normalized[5:7], 16),
    )


def _fill_rect(
    pixels: bytearray,
    image_width: int,
    x0: int,
    y0: int,
    rect_width: int,
    rect_height: int,
    color: RGB,
) -> None:
    for y in range(y0, y0 + rect_height):
        row_start = y * image_width * 3
        for x in range(x0, x0 + rect_width):
            offset = row_start + x * 3
            pixels[offset : offset + 3] = bytes(color)


def _draw_text_centered(
    pixels: bytearray,
    image_width: int,
    x0: int,
    y0: int,
    box_width: int,
    text: str,
    scale: int,
    color: RGB,
) -> None:
    text_width = len(text) * 5 * scale + (len(text) - 1) * scale
    start_x = x0 + max(0, (box_width - text_width) // 2)
    _draw_text(pixels, image_width, start_x, y0, text, scale, color)


def _draw_text(
    pixels: bytearray,
    image_width: int,
    x0: int,
    y0: int,
    text: str,
    scale: int,
    color: RGB,
) -> None:
    cursor = x0
    for char in text.upper():
        glyph = _FONT_5X7.get(char)
        if glyph is None:
            cursor += 6 * scale
            continue
        for row_index, row in enumerate(glyph):
            for col_index, enabled in enumerate(row):
                if enabled == "1":
                    _fill_rect(
                        pixels,
                        image_width,
                        cursor + col_index * scale,
                        y0 + row_index * scale,
                        scale,
                        scale,
                        color,
                    )
        cursor += 6 * scale


def _write_png(path: Path, width: int, height: int, rgb_data: bytes) -> None:
    rows = []
    stride = width * 3
    for y in range(height):
        rows.append(b"\x00" + rgb_data[y * stride : (y + 1) * stride])
    compressed = zlib.compress(b"".join(rows), level=9)

    with path.open("wb") as handle:
        handle.write(b"\x89PNG\r\n\x1a\n")
        _write_chunk(handle, b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        _write_chunk(handle, b"IDAT", compressed)
        _write_chunk(handle, b"IEND", b"")


def _write_chunk(handle, chunk_type: bytes, data: bytes) -> None:
    handle.write(struct.pack(">I", len(data)))
    handle.write(chunk_type)
    handle.write(data)
    checksum = zlib.crc32(chunk_type)
    checksum = zlib.crc32(data, checksum)
    handle.write(struct.pack(">I", checksum & 0xFFFFFFFF))
