"""C. MAPA SKARBU — punkty na siatce trójkątnej, cyfry jako różnice.

Pułapka: w ASCII pierwsza cyfra każdego bajtu jest zawsze z zakresu 2..7,
więc para (pierwsza cyfra, druga cyfra) jako (x, y) daje wąski pas, a nie
mapę. Tutaj cyfry nie są współrzędnymi, tylko **różnicami** współrzędnych:

    d_0 = v_0,  d_i = (v_i - v_{i-1}) mod 16

21 punktów mapy to pary kolejnych różnic: (d_0,d_1), (d_2,d_3), ...
Dekoder czyta współrzędne punktów, liczy różnice i sumuje je mod 16.

Siatka jest trójkątna (dwie rodziny osi pod 60 stopni + przekątne),
osie są podpisane 0..F.
"""

from __future__ import annotations

import math
import xml.etree.ElementTree as ET

HEX = "6B6F6D6172656B7A6D2E6769746875622E696F2F70"

STEP = 6.0
OX, OY = 10.0, 45.0
SQRT3 = math.sqrt(3.0)


def _deltas(hex_str: str) -> list[int]:
    values = [int(ch, 16) for ch in hex_str]
    out = [values[0]]
    out.extend((values[i] - values[i - 1]) % 16 for i in range(1, len(values)))
    return out


def _points(hex_str: str) -> list[tuple[int, int]]:
    deltas = _deltas(hex_str)
    if len(deltas) % 2:
        raise ValueError("łańcuch musi mieć parzystą liczbę cyfr")
    return [(deltas[i], deltas[i + 1]) for i in range(0, len(deltas), 2)]


def _xy(point: tuple[int, int]) -> tuple[float, float]:
    x, y = point
    return OX + STEP * (x + 0.5 * y), OY + STEP * (SQRT3 / 2.0) * y


def render(hex_str: str) -> str:
    points = _points(hex_str)

    parts: list[str] = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="150mm" height="150mm" '
        'viewBox="0 0 150 150">',
        '<rect width="150" height="150" fill="white"/>',
        '<g id="lattice" stroke="black" stroke-width="0.1" fill="none">',
    ]

    for y in range(16):
        x1, y1 = _xy((0, y))
        x2, y2 = _xy((15, y))
        parts.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}"/>')
    for x in range(16):
        x1, y1 = _xy((x, 0))
        x2, y2 = _xy((x, 15))
        parts.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}"/>')
    for x in range(1, 16):
        for y in range(15):
            x1, y1 = _xy((x, y))
            x2, y2 = _xy((x - 1, y + 1))
            parts.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}"/>')
    parts.append("</g>")

    # osie i podpisy 0..F
    parts.append('<g id="axes" fill="black" font-family="monospace" font-size="2.6">')
    for x in range(16):
        px, py = _xy((x, 0))
        parts.append(f'<text x="{px:.2f}" y="{py - 2.4:.2f}" text-anchor="middle">{x:X}</text>')
    for y in range(16):
        px, py = _xy((0, y))
        parts.append(f'<text x="{px - 2.6:.2f}" y="{py + 0.9:.2f}" text-anchor="end">{y:X}</text>')
    ax, ay = _xy((16, 0))
    parts.append(
        f'<line x1="{_xy((0, 0))[0]:.2f}" y1="{_xy((0, 0))[1]:.2f}" '
        f'x2="{ax:.2f}" y2="{ay:.2f}" stroke="black" stroke-width="0.6"/>'
    )
    parts.append(
        f'<polygon points="{ax:.2f},{ay - 1.6:.2f} {ax - 2.2:.2f},{ay - 2.6:.2f} '
        f'{ax - 2.2:.2f},{ay - 0.6:.2f}" fill="black"/>'
    )
    bx, by = _xy((0, 16))
    parts.append(
        f'<line x1="{_xy((0, 0))[0]:.2f}" y1="{_xy((0, 0))[1]:.2f}" '
        f'x2="{bx:.2f}" y2="{by:.2f}" stroke="black" stroke-width="0.6"/>'
    )
    parts.append(
        f'<polygon points="{bx - 1.6:.2f},{by:.2f} {bx - 2.6:.2f},{by + 2.2:.2f} '
        f'{bx - 0.6:.2f},{by + 2.2:.2f}" fill="black"/>'
    )
    parts.append("</g>")

    # trasa
    route = " ".join(f"{_xy(p)[0]:.2f},{_xy(p)[1]:.2f}" for p in points)
    parts.append(
        f'<polyline class="route" points="{route}" fill="none" stroke="black" '
        f'stroke-width="0.4" stroke-dasharray="1.6 1.1" stroke-linejoin="round"/>'
    )

    # punkty i numery
    parts.append('<g id="waypoints">')
    for i, point in enumerate(points, start=1):
        x, y = _xy(point)
        parts.append(f'<circle class="waypoint" cx="{x:.2f}" cy="{y:.2f}" r="1.35" fill="black"/>')
        parts.append(
            f'<text x="{x + 2.1:.2f}" y="{y - 1.9:.2f}" font-family="monospace" '
            f'font-size="2.1" fill="black">{i}</text>'
        )
    parts.append("</g>")

    # start i skarb
    sx, sy = _xy(points[0])
    parts.append(
        f'<circle cx="{sx:.2f}" cy="{sy:.2f}" r="2.7" fill="none" stroke="black" '
        f'stroke-width="0.55"/>'
    )
    ex, ey = _xy(points[-1])
    parts.append(
        f'<g id="treasure" stroke="black" stroke-width="0.9" stroke-linecap="round">'
        f'<line x1="{ex - 2.2:.2f}" y1="{ey - 2.2:.2f}" x2="{ex + 2.2:.2f}" y2="{ey + 2.2:.2f}"/>'
        f'<line x1="{ex - 2.2:.2f}" y1="{ey + 2.2:.2f}" x2="{ex + 2.2:.2f}" y2="{ey - 2.2:.2f}"/>'
        f'</g>'
    )

    parts.append(
        '<text x="75" y="146" font-family="sans-serif" font-size="3.2" '
        'text-anchor="middle" fill="black">'
        'C · MAPA SKARBU — cyfra = różnica współrzędnych, nie współrzędna</text>'
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

    route: list[tuple[float, float]] | None = None
    for element in root.iter():
        if _local_name(element.tag) == "polyline" and element.get("class") == "route":
            route = _parse_points(element.get("points", ""))
            break
    if route is None:
        raise ValueError("brak trasy w SVG")

    deltas: list[int] = []
    for x, y in route:
        lattice_y = (y - OY) / (STEP * SQRT3 / 2.0)
        lattice_x = (x - OX) / STEP - 0.5 * lattice_y
        ix, iy = round(lattice_x), round(lattice_y)
        if not (0 <= ix <= 15 and 0 <= iy <= 15):
            raise ValueError(f"punkt poza siatką: {(ix, iy)}")
        deltas.extend((ix, iy))

    value = 0
    digits = []
    for delta in deltas:
        value = (value + delta) % 16
        digits.append(f"{value:X}")
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
