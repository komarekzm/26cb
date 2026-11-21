"""Runy: kod 4-znakowy zapisany jako cztery znaki, z kluczem na drugiej stronie kartki.

Po co: poprzednia wersja (16 kropek) wymagała przejścia kropki → bity → hex, czyli dwóch
kroków rachunku. Tutaj jest jeden krok: dopasuj kształt do klucza i przepisz cyfrę.
Rysowanie ręką jest też prostsze — runa to dwie, trzy kreski.

Każdy glif to lista łamanych w prostokącie 1 × 2 (x: 0–1, y: 0–2). Kształty są celowo
kanciaste i różnią się liczbą oraz kierunkiem kresek, żeby odręczne kopiowanie było wierne.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET

INK = "#111111"
FAINT = "#e2e0da"
LABEL = "#787774"

# 16 glifów, po jednym na cyfrę hex. Każdy to lista łamanych: [[(x, y), ...], ...]
GLYPHS: dict[str, list[list[tuple[float, float]]]] = {
    "0": [[(0.5, 0.0), (0.5, 2.0)]],                                  # pionowa kresa
    "1": [[(0.5, 0.0), (0.5, 2.0)], [(0.5, 0.0), (1.0, 0.6)]],        # + hak w prawo u góry
    "2": [[(0.5, 0.0), (0.5, 2.0)], [(0.5, 2.0), (1.0, 1.4)]],        # + hak u dołu
    "3": [[(0.5, 0.0), (0.5, 2.0)], [(0.5, 0.3), (1.0, 0.0)], [(0.5, 0.3), (1.0, 0.6)]],  # dwa ramiona w górę
    "4": [[(0.5, 0.0), (0.5, 2.0)], [(0.5, 1.7), (1.0, 2.0)], [(0.5, 1.7), (1.0, 1.4)]],  # dwa ramiona w dół
    "5": [[(0.5, 0.6), (0.5, 2.0)], [(0.5, 0.0), (0.0, 0.6)], [(0.0, 0.6), (0.5, 1.2)]],  # ᚦ
    "6": [[(0.2, 0.0), (0.8, 2.0)], [(0.8, 0.0), (0.2, 2.0)]],        # krzyż ukośny
    "7": [[(0.0, 2.0), (1.0, 0.0)]],                                  # pojedyncza ukośna
    "8": [[(0.0, 0.0), (0.5, 0.9)], [(0.5, 0.9), (1.0, 0.0)]],        # kielich ᚲ
    "9": [[(0.5, 0.0), (0.5, 2.0)], [(0.5, 0.6), (0.0, 0.2)]],        # ramię w lewo
    "a": [[(0.5, 0.0), (0.5, 2.0)], [(0.5, 0.4), (0.0, 0.8)], [(0.5, 0.4), (1.0, 0.8)]],
    "b": [[(0.2, 2.0), (0.5, 0.0)], [(0.5, 0.0), (0.8, 2.0)], [(0.2, 2.0), (0.8, 2.0)]],  # trójkąt
    "c": [[(0.1, 0.0), (0.9, 0.0)], [(0.5, 0.0), (0.5, 2.0)], [(0.1, 2.0), (0.9, 2.0)]],  # belka góra-dół
    "d": [[(0.1, 0.0), (0.9, 0.0)], [(0.1, 0.0), (0.9, 1.0)], [(0.9, 0.0), (0.1, 1.0)],
          [(0.1, 1.0), (0.9, 1.0)]],                                  # klepsydra
    "e": [[(0.5, 0.0), (0.5, 2.0)], [(0.0, 0.8), (1.0, 0.8)]],        # pionowa z poprzeczką
    "f": [[(0.5, 0.0), (1.0, 1.0)], [(1.0, 1.0), (0.5, 2.0)], [(0.5, 2.0), (0.0, 1.0)],
          [(0.0, 1.0), (0.5, 0.0)]],                                  # romb
}


def _valid_code(code: str) -> str:
    code = code.lower()
    if not re.fullmatch(r"[0-9a-f]{4}", code):
        raise ValueError("kod musi mieć 4 znaki z zakresu 0-9 a-f")
    return code


def _glyph(digit: str, x0: float, y0: float, size: float, width: float) -> str:
    """Rysuje glif: każda łamana to jeden <polyline>."""
    parts = [f'<g class="rune">']
    for line in GLYPHS[digit]:
        points = " ".join(f"{x0 + px * size:.2f},{y0 + py * size / 2:.2f}" for px, py in line)
        parts.append(f'<polyline class="glyph" data-digit="{digit}" points="{points}" '
                     f'fill="none" stroke="{INK}" stroke-width="{width}" '
                     f'stroke-linecap="square" stroke-linejoin="miter"/>')
    parts.append("</g>")
    return "".join(parts)


def render_code(code: str, size: float = 64, gap: float = 34) -> str:
    """Cztery runy w rzędzie — to jest to, co ląduje na kartce."""
    code = _valid_code(code)
    pad = size * 0.45
    height = size + pad * 2
    width = pad * 2 + len(code) * size + (len(code) - 1) * gap
    body = [f'<rect width="{width}" height="{height}" fill="#fff"/>']
    for index, digit in enumerate(code):
        x0 = pad + index * (size + gap)
        body.append(f'<line x1="{x0 - gap / 2}" y1="{pad}" x2="{x0 - gap / 2}" y2="{pad + size}" '
                    f'stroke="{FAINT}"/>' if index else "")
        body.append(_glyph(digit, x0, pad, size, size * 0.07))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
            f'width="{width}" height="{height}">{"".join(body)}</svg>')


def render_key(columns: int = 4, size: float = 34) -> str:
    """Klucz: każda runa podpisana swoją cyfrą — to jest cała „tablica ASCII” tej zagadki."""
    rows = (len(GLYPHS) + columns - 1) // columns
    cell_w, cell_h = size * 2.6, size * 1.9
    pad = size * 0.6
    width = pad * 2 + columns * cell_w
    height = pad * 2 + rows * cell_h
    body = [f'<rect width="{width}" height="{height}" fill="#fff"/>']
    for index, digit in enumerate(GLYPHS):
        row, col = divmod(index, columns)
        x0 = pad + col * cell_w + cell_w * 0.12
        y0 = pad + row * cell_h + cell_h * 0.1
        body.append(_glyph(digit, x0, y0, size, size * 0.09))
        body.append(f'<text x="{x0 + size * 1.5}" y="{y0 + size * 0.62}" '
                    f'font-family="monospace" font-size="{size * 0.5}" fill="{LABEL}">{digit}</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
            f'width="{width}" height="{height}">{"".join(body)}</svg>')


# ── odczyt z geometrii (bramka: czy rysunek naprawdę niesie kod) ──────────────
def _normalize(lines: list[list[tuple[float, float]]]) -> tuple:
    """Sprowadza glif do siatki 4 × 8 względem własnej obwiedni — porównujemy kształt."""
    xs = [x for line in lines for x, _ in line]
    ys = [y for line in lines for _, y in line]
    min_x, min_y = min(xs), min(ys)
    span_x = (max(xs) - min_x) or 1.0
    span_y = (max(ys) - min_y) or 1.0
    return tuple(
        tuple((round((x - min_x) / span_x * 4), round((y - min_y) / span_y * 8)) for x, y in line)
        for line in lines
    )


_LOOKUP = {_normalize(lines): digit for digit, lines in GLYPHS.items()}
if len(_LOOKUP) != len(GLYPHS):  # dwa glify nie mogą znaczyć tego samego
    seen: dict[tuple, str] = {}
    for digit, lines in GLYPHS.items():
        key = _normalize(lines)
        if key in seen:
            raise SystemExit(f"glify {seen[key]!r} i {digit!r} mają ten sam kształt")
        seen[key] = digit


def decode(svg: str) -> str:
    """Czyta kod z rysunku: jedna grupa <g class="rune"> = jedna cyfra."""
    root = ET.fromstring(svg)
    groups = [
        element
        for element in root.iter()
        if element.tag.split("}")[-1] == "g" and element.get("class") == "rune"
    ]
    if not groups:
        raise ValueError("brak grup z runami w SVG")

    read = ""
    for group in groups:
        lines = []
        for element in group:
            if element.tag.split("}")[-1] != "polyline":
                continue
            lines.append(
                [tuple(map(float, pair.split(","))) for pair in element.get("points", "").split()]
            )
        key = _normalize(lines)
        if key not in _LOOKUP:
            raise ValueError(f"nieznany kształt: {key}")
        read += _LOOKUP[key]
    return read


if __name__ == "__main__":
    code = "b6e4"
    for name, svg in (("runy-kod", render_code(code)), ("runy-klucz", render_key())):
        open(f"{name}.svg", "w").write(svg)
        print(f"{name:10} {len(svg):6} B")
    print("odczyt kodu :", decode(render_code(code)), "(oczekiwane:", code + ")")
