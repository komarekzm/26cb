"""Labirynt z czterema pieczęciami: kod 4-znakowy ukryty na jedynej drodze.

Idea: mały labirynt (5 × 4 kratki) generowany deterministycznie. Na jedynej drodze
od wejścia do wyjścia leżą cztery runy (te same glify co w `runy/runes.py`). Przejście
labiryntu daje kolejność, klucz run daje cyfry — żadnego liczenia, żadnej binarki.

Rysowanie ręką: siatka 5 × 4 i kilkanaście odcinków ścian. Wszystko w prostokątach,
bez łuków i skosów.
"""

from __future__ import annotations

import random
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "runy"))
import runes  # noqa: E402  (glify trzymamy w jednym miejscu, żeby klucz był ten sam)

WIDTH, HEIGHT = 5, 4  # kratki
CELL = 78  # pikseli na kratkę — przy A4 daje ~14 mm
MARGIN = 26
INK = "#111111"

Point = tuple[int, int]


@dataclass(frozen=True)
class Maze:
    width: int
    height: int
    # dla każdej kratki: które ściany stoją (N, E, S, W)
    walls: dict[Point, set[str]]
    path: list[Point]  # jedyna droga od (0,0) do (w-1,h-1)


def build_maze(width: int = WIDTH, height: int = HEIGHT, seed: int = 7) -> Maze:
    """Labirynt doskonały (drzewo): dokładnie jedna droga między każdą parą kratek."""
    rng = random.Random(seed)
    walls = {(x, y): {"N", "E", "S", "W"} for x in range(width) for y in range(height)}
    opposite = {"N": "S", "S": "N", "E": "W", "W": "E"}
    step = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "W": (-1, 0)}

    start = (0, 0)
    visited = {start}
    stack = [start]
    while stack:
        x, y = stack[-1]
        options = []
        for side, (dx, dy) in step.items():
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited:
                options.append((side, (nx, ny)))
        if not options:
            stack.pop()
            continue
        side, neighbour = rng.choice(options)
        walls[(x, y)].discard(side)
        walls[neighbour].discard(opposite[side])
        visited.add(neighbour)
        stack.append(neighbour)

    # wejście od góry i wyjście dołem — żeby droga była czytelna na papierze
    walls[(0, 0)].discard("N")
    walls[(width - 1, height - 1)].discard("S")

    # jedyna droga: BFS po krawędziach, które nie mają ściany
    path = [start]
    previous: dict[Point, Point] = {}
    frontier = [start]
    seen = {start}
    while frontier:
        x, y = frontier.pop(0)
        if (x, y) == (width - 1, height - 1):
            break
        for side, (dx, dy) in step.items():
            nx, ny = x + dx, y + dy
            if not (0 <= nx < width and 0 <= ny < height):
                continue
            if side in walls[(x, y)]:
                continue
            if (nx, ny) in seen:
                continue
            seen.add((nx, ny))
            previous[(nx, ny)] = (x, y)
            frontier.append((nx, ny))

    node = (width - 1, height - 1)
    route = [node]
    while node != start:
        node = previous[node]
        route.append(node)
    path = route[::-1]
    return Maze(width=width, height=height, walls=walls, path=path)


def seal_cells(maze: Maze, count: int = 4) -> list[Point]:
    """Cztery kratki na drodze, rozłożone równo i nieprzylegające do siebie."""
    if len(maze.path) < count * 2:
        raise SystemExit("labirynt ma za krótką drogę na cztery pieczęcie")
    step = (len(maze.path) - 1) / (count - 1)
    picks: list[Point] = []
    for index in range(count):
        position = round(index * step)
        while maze.path[position] in picks or (
            picks and abs(maze.path.index(picks[-1]) - position) < 2
        ):
            position += 1
        picks.append(maze.path[min(position, len(maze.path) - 1)])
    return picks


def _cell_origin(point: Point) -> tuple[float, float]:
    x, y = point
    return MARGIN + x * CELL, MARGIN + y * CELL


def render(code: str, maze: Maze | None = None) -> str:
    maze = maze or build_maze()
    cells = seal_cells(maze)
    if len(code) != len(cells):
        raise ValueError(f"kod ma {len(code)} znaki, a pieczęci jest {len(cells)}")

    width = MARGIN * 2 + maze.width * CELL
    height = MARGIN * 2 + maze.height * CELL
    body = [f'<rect width="{width}" height="{height}" fill="#fff"/>']

    # ściany: każda krawędź kratki bez sąsiada po tej stronie
    for (x, y), sides in maze.walls.items():
        ox, oy = _cell_origin((x, y))
        lines = {
            "N": (ox, oy, ox + CELL, oy),
            "S": (ox, oy + CELL, ox + CELL, oy + CELL),
            "W": (ox, oy, ox, oy + CELL),
            "E": (ox + CELL, oy, ox + CELL, oy + CELL),
        }
        for side in sides:
            x1, y1, x2, y2 = lines[side]
            body.append(f'<line class="wall" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                        f'stroke="{INK}" stroke-width="5" stroke-linecap="square"/>')

    # pieczęcie: runy w swoich kratkach
    for digit, point in zip(code, cells):
        ox, oy = _cell_origin(point)
        size = CELL * 0.46
        cx, cy = ox + CELL / 2, oy + CELL / 2
        body.append(f'<circle cx="{cx}" cy="{cy}" r="{CELL * 0.36}" fill="#fff" '
                    f'stroke="#c9c6be" stroke-width="1.2"/>')
        body.append(runes._glyph(digit, cx - size / 2, cy - size / 2, size, max(1.5, size * 0.08)))

    # wejście i wyjście
    body.append(f'<text x="{MARGIN}" y="{MARGIN - 10}" font-family="monospace" '
                f'font-size="13" fill="#787774">wejście ↓</text>')
    body.append(f'<text x="{MARGIN + (maze.width - 1) * CELL}" y="{MARGIN + maze.height * CELL + 22}" '
                f'font-family="monospace" font-size="13" fill="#787774">wyjście</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
            f'width="{width}" height="{height}">{"".join(body)}</svg>')


def decode(svg: str, maze: Maze | None = None) -> str:
    """Czyta pieczęcie w kolejności, w jakiej leżą na drodze labiryntu."""
    maze = maze or build_maze()
    root = ET.fromstring(svg)

    found: list[tuple[int, str]] = []  # (pozycja na drodze, cyfra)
    for group in root.iter():
        if group.tag.split("}")[-1] != "g" or group.get("class") != "rune":
            continue
        lines = [
            [tuple(map(float, pair.split(","))) for pair in child.get("points", "").split()]
            for child in group
            if child.tag.split("}")[-1] == "polyline"
        ]
        if not lines:
            continue
        key = runes._normalize(lines)
        if key not in runes._LOOKUP:
            raise ValueError("nieznany kształt pieczęci")
        # pozycja kratki: ze środka obwiedni glifu
        xs = [x for line in lines for x, _ in line]
        ys = [y for line in lines for _, y in line]
        centre = ((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2)
        col = int((centre[0] - MARGIN) // CELL)
        row = int((centre[1] - MARGIN) // CELL)
        if (col, row) not in maze.path:
            raise ValueError("pieczęć leży poza jedyną drogą labiryntu")
        found.append((maze.path.index((col, row)), runes._LOOKUP[key]))

    if len(found) != 4:
        raise ValueError(f"oczekiwano 4 pieczęci, znaleziono {len(found)}")
    found.sort()
    return "".join(digit for _, digit in found)


if __name__ == "__main__":
    import sys as _sys

    code = _sys.argv[1] if len(_sys.argv) > 1 else "c0de"
    maze = build_maze()
    svg = render(code, maze)
    Path(f"labirynt.png.svg").write_text(svg)
    print(f"droga      : {len(maze.path)} kratek: {' → '.join(map(str, maze.path))}")
    print(f"pieczęcie  : {seal_cells(maze)}")
    print(f"kod        : {code}")
    print(f"odczytany  : {decode(svg, maze)}  (zgodny: {decode(svg, maze) == code})")
