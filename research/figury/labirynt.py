"""B. LABIRYNT — jednokorytarzowy labirynt z bramkami.

Trasa to jedna spirala w siatce 24 x 14 pól. Ściany powstają wyłącznie
z trasy: między dwoma sąsiednimi polami stoi ściana, chyba że są kolejnymi
polami trasy. Dzięki temu labirynt jest jednoznaczny (unicursalny).

Kodowanie: na trasie stoją bramki (rombiki). Cyfra hex to liczba pól od
jednej bramki do następnej, licząc pole drugiej bramki. Cyfra 0 to dwie
bramki w jednym polu (romb wypełniony + romb otwarty).

Dekoder czyta ściany i bramki z SVG, odtwarza korytarz i liczy pola.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET

HEX = "6B6F6D6172656B7A6D2E6769746875622E696F2F70"

W, H = 24, 14
C = 6.0
OX, OY = (150.0 - W * C) / 2.0, 33.0


def _spiral_cells(width: int, height: int) -> list[tuple[int, int]]:
    cells: list[tuple[int, int]] = []
    left, right, top, bottom = 0, width - 1, 0, height - 1
    while left <= right and top <= bottom:
        for x in range(left, right + 1):
            cells.append((x, top))
        top += 1
        for y in range(top, bottom + 1):
            cells.append((right, y))
        right -= 1
        if top <= bottom:
            for x in range(right, left - 1, -1):
                cells.append((x, bottom))
            bottom -= 1
        if left <= right:
            for y in range(bottom, top - 1, -1):
                cells.append((left, y))
            left += 1
    return cells


def _path_for(hex_str: str) -> list[tuple[int, int]]:
    n = sum(int(ch, 16) for ch in hex_str) + 1
    cells = _spiral_cells(W, H)
    if n > len(cells):
        raise ValueError("trasa dłuższa niż siatka")
    return cells[:n]


def _center(cell: tuple[int, int]) -> tuple[float, float]:
    x, y = cell
    return OX + (x + 0.5) * C, OY + (y + 0.5) * C


def _wall_segments(path: list[tuple[int, int]]) -> list[tuple[float, float, float, float]]:
    index = {cell: i for i, cell in enumerate(path)}
    path_set = set(path)
    segments: set[tuple[float, float, float, float]] = set()

    def add(x1: float, y1: float, x2: float, y2: float) -> None:
        key = (x1, y1, x2, y2)
        reverse = (x2, y2, x1, y1)
        if reverse < key:
            key = reverse
        segments.add(key)

    for cell in path:
        x, y = cell
        i = index[cell]
        neighbours = (((1, 0), "V"), ((-1, 0), "V"), ((0, 1), "H"), ((0, -1), "H"))
        for (dx, dy), kind in neighbours:
            other = (x + dx, y + dy)
            if other in path_set and abs(index[other] - i) == 1:
                continue
            if kind == "V":
                edge_x = OX + (max(x, x + dx)) * C
                add(edge_x, OY + y * C, edge_x, OY + (y + 1) * C)
            else:
                edge_y = OY + (max(y, y + dy)) * C
                add(OX + x * C, edge_y, OX + (x + 1) * C, edge_y)

    # wejście: górna krawędź pierwszego pola jest otwarta
    sx, sy = path[0]
    entrance = (OX + sx * C, OY + sy * C, OX + (sx + 1) * C, OY + sy * C)
    segments.discard(entrance)
    segments.discard((entrance[2], entrance[3], entrance[0], entrance[1]))
    return sorted(segments)


def _gate_marks(hex_str: str) -> list[int]:
    positions = [0]
    for ch in hex_str:
        positions.append(positions[-1] + int(ch, 16))
    return positions


def render(hex_str: str) -> str:
    path = _path_for(hex_str)
    gates = _gate_marks(hex_str)
    walls = _wall_segments(path)

    parts: list[str] = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="150mm" height="150mm" '
        'viewBox="0 0 150 150">',
        '<rect width="150" height="150" fill="white"/>',
        '<g id="grid" stroke="black" stroke-width="0.12" '
        'stroke-dasharray="0.5 1.3" fill="none">',
    ]
    for x in range(W + 1):
        parts.append(
            f'<line x1="{OX + x * C:.2f}" y1="{OY:.2f}" '
            f'x2="{OX + x * C:.2f}" y2="{OY + H * C:.2f}"/>'
        )
    for y in range(H + 1):
        parts.append(
            f'<line x1="{OX:.2f}" y1="{OY + y * C:.2f}" '
            f'x2="{OX + W * C:.2f}" y2="{OY + y * C:.2f}"/>'
        )
    parts.append("</g>")

    parts.append('<g id="walls" stroke="black" stroke-width="0.62" stroke-linecap="square">')
    for x1, y1, x2, y2 in walls:
        parts.append(f'<line class="wall" x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}"/>')
    parts.append("</g>")

    # bramki: romb wypełniony; przy cyfrze 0 dochodzi romb otwarty
    seen: dict[int, int] = {}
    parts.append('<g id="gates">')
    for index in gates:
        count = seen.get(index, 0)
        seen[index] = count + 1
        cx, cy = _center(path[index])
        half = 1.15 + 0.75 * count
        if count == 0:
            fill, stroke, width = "black", "black", 0.35
        else:
            fill, stroke, width = "white", "black", 0.38
        parts.append(
            f'<polygon class="gate" points="{cx:.2f},{cy - half:.2f} '
            f'{cx + half:.2f},{cy:.2f} {cx:.2f},{cy + half:.2f} '
            f'{cx - half:.2f},{cy:.2f}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{width}"/>'
        )
    parts.append("</g>")

    # wejście
    sx, sy = _center(path[0])
    parts.append(
        f'<g id="entrance"><line x1="{sx:.2f}" y1="{OY - 9:.2f}" x2="{sx:.2f}" '
        f'y2="{OY - 1.2:.2f}" stroke="black" stroke-width="0.9"/>'
        f'<polygon points="{sx - 2.2:.2f},{OY - 3.2:.2f} {sx + 2.2:.2f},{OY - 3.2:.2f} '
        f'{sx:.2f},{OY - 0.4:.2f}" fill="black"/>'
        f'<text x="{sx:.2f}" y="{OY - 11:.2f}" font-family="sans-serif" '
        f'font-size="2.8" text-anchor="middle" fill="black">start</text></g>'
    )

    # meta
    gx, gy = path[-1]
    parts.append(
        f'<g id="goal"><rect class="goal" x="{OX + gx * C + 0.8:.2f}" '
        f'y="{OY + gy * C + 0.8:.2f}" width="{C - 1.6:.2f}" height="{C - 1.6:.2f}" '
        f'fill="none" stroke="black" stroke-width="0.8"/>'
        f'<text x="{OX + (gx + 0.5) * C:.2f}" y="{OY + (gy + 1) * C + 4.2:.2f}" '
        f'font-family="sans-serif" font-size="2.6" text-anchor="middle" '
        f'fill="black">meta</text></g>'
    )

    parts.append(
        '<text x="75" y="146" font-family="sans-serif" font-size="3.2" '
        'text-anchor="middle" fill="black">'
        'B · LABIRYNT — cyfra = ile pól między bramkami (drugie pole włącznie)</text>'
    )
    parts.append("</svg>")
    return "\n".join(parts)


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _edge_key(a: tuple[int, int], b: tuple[int, int]) -> frozenset[tuple[int, int]]:
    return frozenset((a, b))


def decode(svg: str) -> str:
    root = ET.fromstring(svg)

    blocked: set[frozenset[tuple[int, int]]] = set()
    gates: list[tuple[float, float]] = []
    goal: tuple[int, int] | None = None

    for element in root.iter():
        tag = _local_name(element.tag)
        if tag == "line" and element.get("class") == "wall":
            x1 = float(element.get("x1", "0"))
            y1 = float(element.get("y1", "0"))
            x2 = float(element.get("x2", "0"))
            y2 = float(element.get("y2", "0"))
            if abs(y1 - y2) < 1e-6:
                j = round((y1 - OY) / C)
                i = round((x1 - OX) / C)
                if 0 <= i < W and 0 < j <= H:
                    blocked.add(_edge_key((i, j - 1), (i, j)))
            elif abs(x1 - x2) < 1e-6:
                i = round((x1 - OX) / C)
                j = round((y1 - OY) / C)
                if 0 <= j < H and 0 < i <= W:
                    blocked.add(_edge_key((i - 1, j), (i, j)))
        elif tag == "polygon" and element.get("class") == "gate":
            values = [float(v) for v in element.get("points", "").replace(",", " ").split()]
            xs, ys = values[0::2], values[1::2]
            gates.append((sum(xs) / len(xs), sum(ys) / len(ys)))
        elif tag == "rect" and element.get("class") == "goal":
            x = float(element.get("x", "0")) + float(element.get("width", "0")) / 2.0
            y = float(element.get("y", "0")) + float(element.get("height", "0")) / 2.0
            goal = (round((x - OX) / C - 0.5), round((y - OY) / C - 0.5))

    if goal is None:
        raise ValueError("brak mety w SVG")

    start = (0, 0)
    queue = [start]
    parent: dict[tuple[int, int], tuple[int, int] | None] = {start: None}
    while queue:
        cell = queue.pop(0)
        if cell == goal:
            break
        x, y = cell
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            other = (x + dx, y + dy)
            if not (0 <= other[0] < W and 0 <= other[1] < H):
                continue
            if other in parent or _edge_key(cell, other) in blocked:
                continue
            parent[other] = cell
            queue.append(other)

    if goal not in parent:
        raise ValueError("meta nieosiągalna")

    route: list[tuple[int, int]] = []
    current: tuple[int, int] | None = goal
    while current is not None:
        route.append(current)
        current = parent[current]
    route.reverse()

    order = {cell: i for i, cell in enumerate(route)}
    positions = []
    for gx, gy in gates:
        cell = (round((gx - OX) / C - 0.5), round((gy - OY) / C - 0.5))
        if cell not in order:
            raise ValueError(f"bramka poza trasą: {cell}")
        positions.append(order[cell])
    positions.sort()

    digits = []
    for left, right in zip(positions, positions[1:]):
        delta = right - left
        if not 0 <= delta <= 15:
            raise ValueError(f"niejednoznaczna bramka: {delta}")
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
