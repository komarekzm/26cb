"""A. PLASTER MIODU — spiralna ścieżka po siatce heksagonalnej.

Kodowanie: łańcuch hex czyta się jako liczby pól między paciorkami.
Start jest na brzegu plastra, meta w środku. Ścieżka to spirala: wchodzi
o jedno pole do środka po każdym okrążeniu, więc kolejne paciorki leżą na
jednej, nieprzecinającej się linii.

    cyfra = liczba pól od jednego paciorka do następnego

Cyfra 0 daje dwa paciorki w tym samym polu (podwójny pierścień).
Dekoder czyta wyłącznie geometrię SVG: łamaną spiralę i środki paciorków.
"""

from __future__ import annotations

import math
import xml.etree.ElementTree as ET

HEX = "6B6F6D6172656B7A6D2E6769746875622E696F2F70"

# pointy-top hex, axial (q, r)
SQRT3 = math.sqrt(3.0)
DIRS = ((1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1))

# Stała geometria rysunku (mm); 150 x 150 mm.
S = 3.75
CX, CY = 75.0, 68.0


def _ring(radius: int) -> list[tuple[int, int]]:
    """Pola pierścienia `radius` w kolejności zgodnej z ruchem wskazówek."""
    cells: list[tuple[int, int]] = []
    q, r = radius, 0
    for dq, dr in ((0, -1), (-1, 0), (-1, 1), (0, 1), (1, 0), (1, -1)):
        for _ in range(radius):
            cells.append((q, r))
            q += dq
            r += dr
    return cells


def _outward_spiral(rings: int) -> list[tuple[int, int]]:
    """Spirala od środka na zewnątrz; każdy pierścień przechodzony w całości."""
    path = [(0, 0)]
    for radius in range(1, rings + 1):
        ring = _ring(radius)
        previous = path[-1]
        start = next(
            i
            for i, cell in enumerate(ring)
            if max(abs(cell[0] - previous[0]), abs(cell[1] - previous[1]),
                   abs(cell[0] + cell[1] - previous[0] - previous[1])) == 1
        )
        path.extend(ring[start:] + ring[:start])
    return path


def _rings_for(n: int) -> int:
    radius = 0
    while 1 + 3 * radius * (radius + 1) < n:
        radius += 1
    return radius


def _spiral_path(n: int) -> list[tuple[int, int]]:
    """Dokładnie n pól, od brzegu do środka."""
    rings = _rings_for(n)
    outward = _outward_spiral(rings)
    if len(outward) < n:
        raise ValueError("za mało pól w plastrze")
    return outward[:n][::-1]


def _xy(cell: tuple[int, int]) -> tuple[float, float]:
    q, r = cell
    return CX + SQRT3 * S * (q + r / 2.0), CY + 1.5 * S * r


def _gate_indices(hex_str: str) -> list[int]:
    positions = [0]
    for ch in hex_str:
        positions.append(positions[-1] + int(ch, 16))
    return positions


def render(hex_str: str) -> str:
    digits = [int(ch, 16) for ch in hex_str]
    n = sum(digits) + 1
    path = _spiral_path(n)
    rings = _rings_for(n)

    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="150mm" height="150mm" '
        f'viewBox="0 0 150 150">',
        '<rect width="150" height="150" fill="white"/>',
        '<g id="grid" fill="none" stroke="black" stroke-width="0.12">',
    ]

    for radius in range(rings + 1):
        for q, r in _ring(radius):
            x, y = _xy((q, r))
            points = " ".join(
                f"{x + S * math.cos(math.radians(60 * k - 30)):.2f},"
                f"{y + S * math.sin(math.radians(60 * k - 30)):.2f}"
                for k in range(6)
            )
            parts.append(f'<polygon points="{points}"/>')

    parts.append("</g>")

    poly = " ".join(f"{_xy(cell)[0]:.2f},{_xy(cell)[1]:.2f}" for cell in path)
    parts.append(
        f'<polyline class="spiral" points="{poly}" fill="none" stroke="black" '
        f'stroke-width="0.75" stroke-linejoin="round" stroke-linecap="round"/>'
    )

    # paciorki: jeden na każdą granicę cyfry
    gates = _gate_indices(hex_str)
    seen: dict[int, int] = {}
    parts.append('<g id="beads">')
    for index in gates:
        count = seen.get(index, 0)
        seen[index] = count + 1
        x, y = _xy(path[index])
        radius = 1.55 + 0.65 * count
        fill = "white" if count == 0 else "none"
        parts.append(
            f'<circle class="bead" cx="{x:.2f}" cy="{y:.2f}" r="{radius:.2f}" '
            f'fill="{fill}" stroke="black" stroke-width="0.38"/>'
        )
    parts.append("</g>")

    # meta: czarny punkt w dziurce ostatniego paciorka
    ex, ey = _xy(path[-1])
    parts.append(
        f'<g id="goal"><circle cx="{ex:.2f}" cy="{ey:.2f}" r="0.75" fill="black"/></g>'
    )


    # start: strzałka wchodząca w plaster od zewnątrz
    sx, sy = _xy(path[0])
    dx, dy = sx - CX, sy - CY
    length = math.hypot(dx, dy) or 1.0
    ux, uy = dx / length, dy / length
    ax, ay = sx + ux * 8.0, sy + uy * 8.0
    bx, by = sx + ux * 2.3, sy + uy * 2.3
    px, py = -uy, ux
    base_x, base_y = bx - ux * 1.8, by - uy * 1.8
    parts.append(
        f'<g id="start"><line x1="{ax:.2f}" y1="{ay:.2f}" x2="{bx:.2f}" '
        f'y2="{by:.2f}" stroke="black" stroke-width="0.9"/>'
        f'<polygon points="{bx:.2f},{by:.2f} '
        f'{base_x + px * 1.9:.2f},{base_y + py * 1.9:.2f} '
        f'{base_x - px * 1.9:.2f},{base_y - py * 1.9:.2f}" fill="black"/>'
        f'<text x="{ax + ux * 4.0:.2f}" y="{ay + uy * 4.0:.2f}" '
        f'font-family="sans-serif" font-size="2.6" text-anchor="middle" fill="black">start</text></g>'
    )

    parts.append(
        '<text x="75" y="146" font-family="sans-serif" font-size="3.2" '
        'text-anchor="middle" fill="black">'
        'A · PLASTER MIODU — cyfra = ile pól od paciorka do paciorka; 0 = dwa pierścienie</text>'
    )
    parts.append("</svg>")
    return "\n".join(parts)


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _parse_points(value: str) -> list[tuple[float, float]]:
    numbers = [float(v) for v in value.replace(",", " ").split()]
    return list(zip(numbers[0::2], numbers[1::2]))


def decode(svg: str) -> str:
    root = ET.fromstring(svg)

    spiral: list[tuple[float, float]] | None = None
    beads: list[tuple[float, float]] = []
    for element in root.iter():
        tag = _local_name(element.tag)
        if tag == "polyline" and element.get("class") == "spiral":
            spiral = _parse_points(element.get("points", ""))
        elif tag == "circle" and element.get("class") == "bead":
            beads.append((float(element.get("cx", "0")), float(element.get("cy", "0"))))

    if spiral is None:
        raise ValueError("brak spirali w SVG")
    if not beads:
        raise ValueError("brak paciorków w SVG")

    path: list[tuple[int, int]] = []
    for x, y in spiral:
        r = (y - CY) / (1.5 * S)
        q = (x - CX) / (SQRT3 * S) - r / 2.0
        path.append((round(q), round(r)))

    indices = []
    for bx, by in beads:
        best = min(
            range(len(path)),
            key=lambda i: (_xy(path[i])[0] - bx) ** 2 + (_xy(path[i])[1] - by) ** 2,
        )
        indices.append(best)
    indices.sort()

    digits = []
    for left, right in zip(indices, indices[1:]):
        delta = right - left
        if not 0 <= delta <= 15:
            raise ValueError(f"niejednoznaczny paciorek: {delta}")
        digits.append(f"{delta:X}")

    return "".join(digits)


if __name__ == "__main__":
    from pathlib import Path

    svg = render(HEX)
    target = Path(__file__).with_suffix(".svg")
    target.write_text(svg, encoding="utf-8")
    decoded = decode(svg)
    assert decoded == HEX, (decoded, HEX)
    print("OK", decoded)
    print("SVG", target)
