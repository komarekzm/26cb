"""Pięć wariantów rysunku dla kodu 4-znakowego (16 bitów).

Wspólny ładunek: kod hex `b6e4` = 16 bitów = 1011 0110 1110 0100. Każdy wariant
zapisuje te same 16 bitów innym gestem, żeby dało się je narysować ołówkiem,
i każdy ma `decode()`, który odczytuje bity z geometrii SVG (nie z metadanych).

Uruchomienie: python3 marks.py  → wypisze round-trip i zapisze SVG.
"""

from __future__ import annotations

import itertools
import math
import re
import xml.etree.ElementTree as ET

CODE = "b6e4"
INK = "#111111"
FAINT = "#c9c6be"
LABEL = "#787774"


# ── wspólne ───────────────────────────────────────────────────────────────────
def bits(code: str) -> list[int]:
    """Kod hex → 16 bitów w kolejności czytania (od najstarszego bitu)."""
    if not re.fullmatch(r"[0-9a-fA-F]{4}", code):
        raise ValueError("kod musi mieć 4 znaki z zakresu 0-9 a-f")
    return [(int(char, 16) >> shift) & 1 for char in code for shift in (3, 2, 1, 0)]


def from_bits(values: list[int]) -> str:
    if len(values) != 16:
        raise ValueError(f"oczekiwano 16 bitów, jest {len(values)}")
    return "".join(f"{sum(bit << (3 - i) for i, bit in enumerate(values[j : j + 4])):x}" for j in range(0, 16, 4))


def _local(tag: str) -> str:
    return tag.split("}")[-1]


def _svg(width: float, height: float, body: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}">{body}</svg>'
    )


# ── A: kropki 4 × 4 ───────────────────────────────────────────────────────────
def render_dots(code: str, cell: float = 22) -> str:
    values = bits(code)
    pad = cell
    size = pad * 2 + cell * 3
    parts = [f'<rect width="{size}" height="{size}" fill="#fff"/>']
    for index, bit in enumerate(values):
        row, col = divmod(index, 4)
        x, y = pad + col * cell, pad + row * cell
        fill = INK if bit else "#fff"
        parts.append(
            f'<circle class="dot" cx="{x}" cy="{y}" r="{cell * 0.28}" fill="{fill}" '
            f'stroke="{INK}" stroke-width="1.4"/>'
        )
    # strzałka czytania: rząd po rzędzie, z lewej do prawej
    parts.append(f'<text x="{pad}" y="{size - cell * 0.15}" font-family="monospace" '
                 f'font-size="{cell * 0.4}" fill="{LABEL}">czytaj rzędami →</text>')
    return _svg(size, size, "".join(parts))


def decode_dots(svg: str) -> str:
    root = ET.fromstring(svg)
    dots = [
        (float(e.get("cy")), float(e.get("cx")), 1 if e.get("fill") == INK else 0)
        for e in root.iter()
        if _local(e.tag) == "circle" and e.get("class") == "dot"
    ]
    dots.sort()
    return from_bits([bit for _, _, bit in dots])


# ── B: kratki 4 × 4 ───────────────────────────────────────────────────────────
def render_cells(code: str, cell: float = 18) -> str:
    values = bits(code)
    pad = cell * 0.8
    size = pad * 2 + cell * 4
    parts = [f'<rect width="{size}" height="{size}" fill="#fff"/>']
    for index, bit in enumerate(values):
        row, col = divmod(index, 4)
        x, y = pad + col * cell, pad + row * cell
        fill = INK if bit else "#fff"
        parts.append(
            f'<rect class="cell" x="{x}" y="{y}" width="{cell}" height="{cell}" '
            f'fill="{fill}" stroke="{INK}" stroke-width="1"/>'
        )
    return _svg(size, size, "".join(parts))


def decode_cells(svg: str) -> str:
    root = ET.fromstring(svg)
    cells = [
        (float(e.get("y")), float(e.get("x")), 1 if e.get("fill") == INK else 0)
        for e in root.iter()
        if _local(e.tag) == "rect" and e.get("class") == "cell"
    ]
    cells.sort()
    return from_bits([bit for _, _, bit in cells])


# ── C: tarcza (4 pierścienie × 4 sektory) ─────────────────────────────────────
def render_shield(code: str, radius: float = 66) -> str:
    """Każda cyfra to jeden pierścień; wypełniona kropka w sektorze = 1."""
    values = bits(code)
    pad = 18
    size = radius * 2 + pad * 2
    center = size / 2
    parts = [f'<rect width="{size}" height="{size}" fill="#fff"/>']
    for ring in range(4):
        parts.append(f'<circle cx="{center}" cy="{center}" r="{radius * (ring + 1) / 4}" '
                     f'fill="none" stroke="{FAINT}"/>')
    for index, bit in enumerate(values):
        ring, sector = divmod(index, 4)
        angle = math.radians(-45 + sector * 90)  # NE, NW, SW, SE — zgodnie z ruchem zegara
        r = radius * (ring + 0.5) / 4
        cx, cy = center + math.cos(angle) * r, center + math.sin(angle) * r
        if bit:
            parts.append(f'<circle class="sector" cx="{cx}" cy="{cy}" r="{radius * 0.075}" '
                         f'fill="{INK}"/>')
        else:
            parts.append(f'<circle cx="{cx}" cy="{cy}" r="{radius * 0.075}" fill="none" '
                         f'stroke="{FAINT}"/>')
    parts.append(f'<text x="{center}" y="{size - 6}" font-family="monospace" font-size="11" '
                 f'fill="{LABEL}" text-anchor="middle">od środka na zewnątrz, 4 sektory na pierścień</text>')
    return _svg(size, size, "".join(parts))


def decode_shield(svg: str) -> str:
    root = ET.fromstring(svg)
    marks = []
    for element in root.iter():
        if _local(element.tag) != "circle" or element.get("class") != "sector":
            continue
        marks.append((float(element.get("cx")), float(element.get("cy"))))
    # środek i promień odtwarzamy z obwiedni wypełnionych kropek jest zawodne —
    # bierzemy środek z okręgów siatki
    rings = [
        float(e.get("r"))
        for e in root.iter()
        if _local(e.tag) == "circle" and e.get("stroke") == FAINT and e.get("fill") == "none"
    ]
    if not rings:
        raise ValueError("brak pierścieni siatki")
    outer = max(rings)
    # środek: z okręgów siatki (cx, cy)
    grid = [
        (float(e.get("cx")), float(e.get("cy")))
        for e in root.iter()
        if _local(e.tag) == "circle" and e.get("stroke") == FAINT and e.get("fill") == "none"
    ]
    center_x, center_y = grid[0]
    values = [0] * 16
    for cx, cy in marks:
        dx, dy = cx - center_x, cy - center_y
        r = math.hypot(dx, dy)
        ring = min(3, max(0, round((r * 4 / outer) - 0.5)))
        angle = (math.degrees(math.atan2(dy, dx)) + 45) % 360
        sector = round(angle / 90) % 4
        values[ring * 4 + sector] = 1
    return from_bits(values)


# ── D: pieczęć (16 promieni w kręgu, długi = 1) ───────────────────────────────
def render_seal(code: str, radius: float = 54) -> str:
    values = bits(code)
    center = radius + 22
    size = center * 2
    parts = [f'<rect width="{size}" height="{size}" fill="#fff"/>',
             f'<circle cx="{center}" cy="{center}" r="{radius}" fill="none" stroke="{FAINT}"/>']
    for index, bit in enumerate(values):
        # start u góry, zgodnie z ruchem wskazówek zegara
        angle = math.radians(-90 + index * 22.5)
        length = radius * (1.0 if bit else 0.62)
        x2 = center + math.cos(angle) * length
        y2 = center + math.sin(angle) * length
        parts.append(
            f'<line class="tick" x1="{center}" y1="{center}" x2="{x2}" y2="{y2}" '
            f'stroke="{INK}" stroke-width="{3.2 if bit else 1.1}"/>'
        )
    parts.append(f'<circle cx="{center}" cy="{center}" r="2.5" fill="{INK}"/>')
    return _svg(size, size, "".join(parts))


def decode_seal(svg: str) -> str:
    root = ET.fromstring(svg)
    ticks = []
    for element in root.iter():
        if _local(element.tag) != "line" or element.get("class") != "tick":
            continue
        x1, y1 = float(element.get("x1")), float(element.get("y1"))
        x2, y2 = float(element.get("x2")), float(element.get("y2"))
        ticks.append((math.hypot(x2 - x1, y2 - y1), float(element.get("stroke-width"))))
    longest = max(length for length, _ in ticks)
    values = [1 if width > 2.0 else 0 for length, width in ticks]
    if len([v for v in values if v]) == 0:
        raise ValueError("brak długich promieni")
    return from_bits(values)


# ── E: domino (4 kafle, każdy 2 × 2 oczka) ────────────────────────────────────
def render_domino(code: str, tile: float = 30) -> str:
    values = bits(code)
    gap = tile * 0.4
    width = tile * 4 + gap * 3 + tile * 0.6
    height = tile + tile * 0.6
    parts = [f'<rect width="{width}" height="{height}" fill="#fff"/>']
    for index in range(4):
        x = tile * 0.3 + index * (tile + gap)
        parts.append(
            f'<rect class="tile" x="{x}" y="{tile * 0.3}" width="{tile}" height="{tile}" '
            f'rx="{tile * 0.08}" fill="#fff" stroke="{INK}" stroke-width="1.6"/>'
        )
        for corner in range(4):
            dx, dy = divmod(corner, 2)  # 0,0 / 0,1 / 1,0 / 1,1
            cx = x + tile * (0.28 + 0.44 * dx)
            cy = tile * 0.3 + tile * (0.28 + 0.44 * dy)
            if values[index * 4 + corner]:
                parts.append(f'<circle class="pip" cx="{cx}" cy="{cy}" r="{tile * 0.11}" fill="{INK}"/>')
            else:
                parts.append(f'<circle cx="{cx}" cy="{cy}" r="{tile * 0.11}" fill="none" '
                             f'stroke="{FAINT}"/>')
    return _svg(width, height, "".join(parts))


def decode_domino(svg: str) -> str:
    """Dla każdego kafla sprawdzamy cztery narożne oczka — wypełnione czy nie."""
    root = ET.fromstring(svg)
    tiles = [
        (float(e.get("x")), float(e.get("y")), float(e.get("width")))
        for e in root.iter()
        if _local(e.tag) == "rect" and e.get("class") == "tile"
    ]
    tiles.sort()
    pips = [
        (float(e.get("cx")), float(e.get("cy")))
        for e in root.iter()
        if _local(e.tag) == "circle" and e.get("class") == "pip"
    ]
    values = []
    for x, y, size in tiles:
        for corner in range(4):
            dx, dy = divmod(corner, 2)
            cx = x + size * (0.28 + 0.44 * dx)
            cy = y + size * (0.28 + 0.44 * dy)
            values.append(1 if any(abs(px - cx) < 1 and abs(py - cy) < 1 for px, py in pips) else 0)
    return from_bits(values)


VARIANTS = {
    "A-kropki": (render_dots, decode_dots),
    "B-kratki": (render_cells, decode_cells),
    "C-tarcza": (render_shield, decode_shield),
    "D-pieczec": (render_seal, decode_seal),
    "E-domino": (render_domino, decode_domino),
}


if __name__ == "__main__":
    for name, (render, decode) in VARIANTS.items():
        svg = render(CODE)
        open(f"{name}.svg", "w").write(svg)
        try:
            read = decode(svg)
            status = "OK  " if read == CODE else f"ZŁY {read}"
        except Exception as exc:  # dekoder ma prawo nie umieć — mówimy to wprost
            status = f"BŁĄD {exc}"
        print(f"{name:12} {status}")
