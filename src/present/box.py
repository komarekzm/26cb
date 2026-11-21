"""Siatka 4 × 4: kod czteroznakowy zapisany jako 16 kropek.

Wagi kolumn to 1, 2, 4, 8 (od lewej). W każdym rzędzie suma wag zamalowanych kropek daje
jedną cyfrę kodu; wiersze czytamy z góry na dół. Cztery rzędy = cztery znaki.

Dlaczego tak: kod ma cztery znaki, więc kartka nie musi nieść całego adresu — domena
jest napisana wprost, a rysunek niesie tylko ogon. To 16 kropek do postawienia ołówkiem,
a nie 168.
"""

from __future__ import annotations

import re
import secrets
import string
import xml.etree.ElementTree as ET

# Domyślnie pięć kolumn (1 2 4 8 16 → cały alfabet), ale da się zejść do czterech,
# gdy kod mieści się w literach a–o: 1+2+4+8 = 15.
WEIGHTS = (1, 2, 4, 8, 16)
LETTERS = string.ascii_lowercase  # 1 = a, 2 = b, … 26 = z
INK = "#111111"
FAINT = "#c9c6be"
GRID = "#efeeea"
LABEL = "#787774"
HEX_DIGITS = string.hexdigits.lower()[:16]  # 0-9a-f


def valid_code(code: str) -> str:
    """Kod to cztery małe litery — numer litery w alfabecie jest tym, co niesie siatka."""
    code = code.strip().lower()
    if not re.fullmatch(r"[a-z]{4}", code):
        raise ValueError(f"kod musi mieć 4 małe litery, jest {code!r}")
    return code


def random_code(rng=None) -> str:
    """Losowy kod z samych cyfr.

    Tylko cyfry, bo adres na GitHub Pages jest wrażliwy na wielkość liter: `/286D`
    daje 404, gdy strona stoi pod `/286d`, a dwóch repozytoriów różniących się tylko
    wielkością litery nie da się mieć (nazwy repo są niewrażliwe na wielkość).
    Bez liter problem znika: kod wpisany z Caps Lockiem i tak trafi.
    """
    source = rng or secrets
    words = {"test", "abcd", "deko", "kota", "masa", "lama", "krem", "kark", "takt"}
    while True:
        code = "".join(source.choice(LETTERS) for _ in range(4))
        if code not in words and len(set(code)) > 2:
            return code


def digits(code: str) -> list[int]:
    """Litera → numer w alfabecie: a = 1, b = 2, … z = 26."""
    return [LETTERS.index(char) + 1 for char in valid_code(code)]


def fits(code: str, weights: tuple[int, ...]) -> bool:
    """Czy każda litera kodu mieści się w sumie tych wag."""
    limit = sum(weights)
    return all(value <= limit for value in digits(code))


def _values(svg: str) -> list[int]:
    """Sumy wag w każdym rzędzie — jedyne, co siatka naprawdę niesie."""
    root = ET.fromstring(svg)
    weights = [
        (float(element.get("x")), int(element.text))
        for element in root.iter()
        if element.tag.split("}")[-1] == "text" and element.get("class") == "weight"
    ]
    if not weights:
        raise ValueError("rysunek nie podpisuje wag kolumn")
    ordered = [weight for _, weight in sorted(weights)]

    dots = [
        (int(element.get("data-row")), int(element.get("data-col")),
         int(element.get("data-filled")))
        for element in root.iter()
        if element.tag.split("}")[-1] == "circle" and element.get("class") == "dot"
    ]
    if len(dots) != 4 * len(ordered):
        raise ValueError(f"oczekiwano {4 * len(ordered)} kropek, jest {len(dots)}")

    values = [0, 0, 0, 0]
    for row, col, filled in dots:
        if filled:
            values[row] += ordered[col]
    return values


def decode_hex(svg: str) -> str:
    """Odczyt siatki jako czterech cyfr hex — bez litery alfabetu pośrodku."""
    values = _values(svg)
    if any(not 0 <= value <= 15 for value in values):
        raise ValueError(f"suma poza zakresem jednej cyfry hex: {values}")
    return "".join(f"{value:x}" for value in values)


def render_hex(code: str, cell: float = 92, weights: tuple[int, ...] = (1, 2, 4, 8)) -> str:
    """Siatka dla kodu zapisanego cyframi hex: 26cb → sumy 2, 6, 12, 11."""
    code = code.strip().lower()
    if not re.fullmatch(r"[0-9a-f]{4}", code):
        raise ValueError(f"kod musi mieć 4 cyfry hex, jest {code!r}")
    return _render([int(char, 16) for char in code], cell, weights)


def render(code: str, cell: float = 92, weights: tuple[int, ...] = WEIGHTS) -> str:
    """Siatka z podpisanymi wagami kolumn — dokładnie to, co rysujesz na kartce."""
    if not fits(code, weights):
        raise ValueError(f"kod {code} nie mieści się w siatce o sumie wag {sum(weights)}")
    return _render(digits(code), cell, weights)


def _render(values: list[int], cell: float, weights: tuple[int, ...]) -> str:
    pad_left = cell * 0.9
    pad_top = cell * 1.0
    width = pad_left + cell * len(weights) + cell * 0.2
    height = pad_top + cell * 4 + cell * 0.2
    parts = [f'<rect width="{width}" height="{height}" fill="#fff"/>']

    font = cell * 0.34
    for col, weight in enumerate(weights):
        cx = pad_left + col * cell + cell / 2
        parts.append(f'<text class="weight" x="{cx}" y="{pad_top - cell * 0.32}" '
                     f'font-family="monospace" font-size="{font}" fill="{LABEL}" '
                     f'text-anchor="middle">{weight}</text>')
    for row, value in enumerate(values):
        for col, weight in enumerate(weights):
            cx = pad_left + col * cell + cell / 2
            cy = pad_top + row * cell + cell / 2
            filled = 1 if value & weight else 0
            # pusta kropka to jasny okrąg — widać, gdzie stawiać, i nie myli się z resztą
            parts.append(
                f'<circle class="dot" data-row="{row}" data-col="{col}" data-filled="{filled}" '
                f'cx="{cx}" cy="{cy}" r="{cell * 0.26}" '
                f'fill="{INK if filled else "#fff"}" stroke="{INK}" stroke-width="2"/>'
            )
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
            f'width="{width}" height="{height}" role="img" '
            f'aria-label="Kod zapisany jako siatka czterech na cztery">{"".join(parts)}</svg>')


def decode(svg: str) -> str:
    """Odczyt siatki jako liter alfabetu (1 = a … 26 = z)."""
    values = _values(svg)
    if any(not 1 <= value <= 26 for value in values):
        raise ValueError(f"suma poza alfabetem: {values}")
    return "".join(LETTERS[value - 1] for value in values)


def render_key(weights: tuple[int, ...] = WEIGHTS, cell: float = 34) -> str:
    """Legenda: numer litery (w hexie) i wagi kolumn — to wszystko, czego trzeba."""
    limit = sum(weights)
    columns = 7
    rows = (len(LETTERS) + columns - 1) // columns
    width = cell * (columns * 3.1)
    height = cell * (rows * 0.78 + 2.6)
    parts = [f'<rect width="{width}" height="{height}" fill="#fff"/>']

    for index, letter_ in enumerate(LETTERS):
        row, col = divmod(index, columns)
        x = cell * 0.5 + col * cell * 3.1
        y = cell * 1.0 + row * cell * 0.78
        dim = "" if index + 1 <= limit else ' opacity="0.35"'
        parts.append(f'<text x="{x}" y="{y}" font-family="monospace" font-size="{cell * 0.46}" '
                     f'fill="{LABEL}"{dim}>{f"{index + 1:X}"}·</text>')
        parts.append(f'<text x="{x + cell * 1.0}" y="{y}" font-family="monospace" '
                     f'font-size="{cell * 0.52}" fill="#2f3437"{dim}>{letter_}</text>')

    y = cell * 1.0 + rows * cell * 0.78 + cell * 0.9
    parts.append(f'<text x="{cell * 0.5}" y="{y}" font-family="monospace" font-size="{cell * 0.44}" '
                 f'fill="#2f3437">kolumny siatki: {" ".join(map(str, weights))} '
                 f'· maksimum {limit:X}</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
            f'width="{width}" height="{height}">{"".join(parts)}</svg>')


if __name__ == "__main__":
    import sys

    code = sys.argv[1] if len(sys.argv) > 1 else "9f2b"
    print(f"kod        : {valid_code(code)}")
    for row, value in enumerate(digits(code)):
        marked = [str(w) for w in WEIGHTS if value & w]
        print(f"  rząd {row + 1}  : {' + '.join(marked) or '0':18} = {value:2} → {LETTERS[value - 1]}")
    print(f"odczyt     : {decode(render(code))}")
    print(f"losowy kod : {random_code()}")
