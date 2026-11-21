"""Hex zapisany jako figura 2D: profil terenu na siatce kolumn × 16 poziomów.

Kolumna = jeden znak hex, wysokość kolumny = jego wartość (0–F). Czterdzieści dwa znaki
dają grzbiet, który czyta się jak mapa: liczysz kratki w górę od podstawy i odczytujesz
cyfrę. Ta sama informacja co ciąg hex, tylko do zmierzenia okiem.

Profil łamie się na dwa rzędy (jak tekst w kolumnach gazety): dzięki temu kratki są
cztery razy większe i da się je policzyć na wydruku, zamiast zgadywać przy linijce.

Dlaczego nie „współrzędne z par cyfr”: cały adres to ASCII, więc każde dwie cyfry
zaczynają się od 6 albo 7 i punkty układają się w pionową kreskę. Wysokości rozkładają
się równo, bo druga cyfra bajtu faktycznie się zmienia.
"""

from __future__ import annotations

INK = "#111111"
GRID_LINE = "#efeeea"
LABEL = "#787774"
FILL = "#f6f5f1"

LEVELS = 16  # 0..F


def nibbles(text: str) -> list[int]:
    return [int(char, 16) for char in text]


def heights(hex_code: str) -> list[int]:
    return nibbles(hex_code)


def hex_from_heights(heights_: list[int]) -> str:
    """Odczyt z rysunku: kolumna po kolumnie, wysokość w kratkach to cyfra."""
    return "".join(f"{value:X}" for value in heights_)


def rows(values: list[int], per_row: int) -> list[list[int]]:
    return [values[i : i + per_row] for i in range(0, len(values), per_row)]


def svg(hex_code: str, cell: int = 30, per_row: int = 21) -> str:
    """Rysunek: siatka z podpisanymi poziomami, grzbiet, numeracja kolumn ciągła."""
    values = heights(hex_code)
    chunks = rows(values, per_row)

    pad_left, pad_top = cell * 0.95, cell * 0.35
    row_height = LEVELS * cell
    gap = cell * 1.2
    width = pad_left + per_row * cell + cell * 0.3
    height = pad_top + len(chunks) * (row_height + gap) + cell * 0.9

    parts: list[str] = []
    number = 0
    for row_index, chunk in enumerate(chunks):
        base_y = pad_top + row_index * (row_height + gap)
        baseline = base_y + row_height

        def level_y(level: int) -> float:
            return baseline - level * cell

        columns = len(chunk)
        grid = "\n".join(
            f'<line x1="{pad_left}" y1="{level_y(level)}" x2="{pad_left + columns * cell}" '
            f'y2="{level_y(level)}" stroke="{GRID_LINE}" class="grid"/>'
            for level in range(LEVELS + 1)
        ) + "\n" + "\n".join(
            f'<line x1="{pad_left + index * cell}" y1="{level_y(0)}" '
            f'x2="{pad_left + index * cell}" y2="{level_y(LEVELS)}" stroke="{GRID_LINE}"/>'
            for index in range(columns + 1)
        )

        spine = [
            (pad_left + index * cell + cell / 2, level_y(value)) for index, value in enumerate(chunk)
        ]
        outline = " ".join(
            [
                f"M {spine[0][0]} {level_y(0)}",
                *[f"L {px} {py}" for px, py in spine],
                f"L {spine[-1][0]} {level_y(0)} Z",
            ]
        )
        markers = "\n".join(
            f'<rect class="marker" x="{px - cell * 0.09}" y="{py - cell * 0.09}" '
            f'width="{cell * 0.18}" height="{cell * 0.18}" fill="{INK}"/>'
            for px, py in spine
        )
        levels = "\n".join(
            f'<text x="{pad_left - cell * 0.45}" y="{level_y(level) + cell * 0.16}">'
            f"{level:X}</text>"
            for level in (0, 4, 8, 12, 15)
        )
        numbers = "\n".join(
            f'<text x="{pad_left + index * cell + cell * 0.2}" y="{level_y(0) + cell * 0.62}">'
            f"{number + index + 1}</text>"
            for index in range(0, columns, 5)
        )
        number += columns

        parts.append(
            f"""<g>
    <g stroke-width="1">{grid}</g>
    <path d="{outline}" fill="{FILL}" stroke="{INK}" stroke-width="1.3" stroke-linejoin="round"/>
    {markers}
    <line class="baseline" x1="{pad_left}" y1="{baseline}" x2="{pad_left + columns * cell}"
          y2="{baseline}" stroke="{INK}" stroke-width="1.3"/>
    {levels}
    {numbers}
  </g>"""
        )

    font = cell * 0.36
    body = "\n".join(parts)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}"
     width="{width}" height="{height}" class="figure-svg" role="img"
     aria-label="Adres zapisany jako profil: wysokość kolumny to kolejna cyfra hex">
  <style>
    text {{ font: 400 {font}px "JetBrains Mono", ui-monospace, monospace; fill: {LABEL}; }}
  </style>
  <rect width="{width}" height="{height}" fill="#ffffff"/>
  {body}
</svg>"""
