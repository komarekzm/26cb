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

WEIGHTS = (1, 2, 4, 8)  # kolejność kolumn od lewej
INK = "#111111"
FAINT = "#c9c6be"
GRID = "#efeeea"
LABEL = "#787774"
HEX_DIGITS = string.hexdigits.lower()[:16]  # 0-9a-f


def valid_code(code: str) -> str:
    code = code.strip().lower()
    if not re.fullmatch(r"[0-9a-f]{4}", code):
        raise ValueError(f"kod musi mieć 4 znaki z zakresu 0-9 a-f, jest {code!r}")
    return code


def random_code(rng=None) -> str:
    """Losowy kod z samych cyfr.

    Tylko cyfry, bo adres na GitHub Pages jest wrażliwy na wielkość liter: `/286D`
    daje 404, gdy strona stoi pod `/286d`, a dwóch repozytoriów różniących się tylko
    wielkością litery nie da się mieć (nazwy repo są niewrażliwe na wielkość).
    Bez liter problem znika: kod wpisany z Caps Lockiem i tak trafi.
    """
    source = rng or secrets
    plain = {"1248", "8421", "1234", "4321", "1111", "2222", "0000", "9999"}
    while True:
        code = "".join(source.choice("0123456789") for _ in range(4))
        if code not in plain and len(set(code)) > 2:
            return code


def digits(code: str) -> list[int]:
    return [int(char, 16) for char in valid_code(code)]


def render(code: str, cell: float = 92) -> str:
    """Siatka z podpisanymi wagami kolumn — dokładnie to, co rysujesz na kartce."""
    values = digits(code)
    pad_left = cell * 0.9
    pad_top = cell * 1.0
    width = pad_left + cell * 4 + cell * 0.2
    height = pad_top + cell * 4 + cell * 0.2
    parts = [f'<rect width="{width}" height="{height}" fill="#fff"/>']

    font = cell * 0.34
    for col, weight in enumerate(WEIGHTS):
        cx = pad_left + col * cell + cell / 2
        parts.append(f'<text class="weight" x="{cx}" y="{pad_top - cell * 0.32}" '
                     f'font-family="monospace" font-size="{font}" fill="{LABEL}" '
                     f'text-anchor="middle">{weight}</text>')
    for row, value in enumerate(values):
        for col, weight in enumerate(WEIGHTS):
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
    """Odczyt z geometrii: rząd i kolumna z położenia kropki, wypełnienie z atrybutu."""
    root = ET.fromstring(svg)
    dots = [
        (int(element.get("data-row")), int(element.get("data-col")),
         int(element.get("data-filled")))
        for element in root.iter()
        if element.tag.split("}")[-1] == "circle" and element.get("class") == "dot"
    ]
    if len(dots) != 16:
        raise ValueError(f"oczekiwano 16 kropek, jest {len(dots)}")
    dots.sort()
    values = [0, 0, 0, 0]
    for row, col, filled in dots:
        if filled:
            values[row] += WEIGHTS[col]
    return "".join(f"{value:x}" for value in values)


def render_key(cell: float = 40, letters: bool = False) -> str:
    """Klucz na odwrotną stronę: waga każdej kolumny i co znaczą sumy powyżej dziewięciu."""
    rows = [
        ("kolumna 1", "1", "kropka w pierwszej kolumnie"),
        ("kolumna 2", "2", "kropka w drugiej kolumnie"),
        ("kolumna 3", "4", "kropka w trzeciej kolumnie"),
        ("kolumna 4", "8", "kropka w czwartej kolumnie"),
    ]
    width, height = cell * 16, cell * 6.2
    parts = [f'<rect width="{width}" height="{height}" fill="#fff"/>']
    for index, (label, weight, note) in enumerate(rows):
        y = cell * 1.1 + index * cell * 1.15
        parts.append(f'<circle cx="{cell * 0.9}" cy="{y - cell * 0.12}" r="{cell * 0.2}" fill="{INK}"/>')
        parts.append(f'<text x="{cell * 1.5}" y="{y}" font-family="monospace" font-size="{cell * 0.42}" '
                     f'fill="{LABEL}">{weight}</text>')
        parts.append(f'<text x="{cell * 2.6}" y="{y}" font-family="monospace" font-size="{cell * 0.4}" '
                     f'fill="#2f3437">{note}</text>')
    if letters:
        parts.append(f'<text x="{cell * 0.6}" y="{cell * 5.6}" font-family="monospace" '
                     f'font-size="{cell * 0.38}" fill="{LABEL}">'
                     f'sumuj w rzędzie · 10=a 11=b 12=c 13=d 14=e 15=f</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
            f'width="{width}" height="{height}">{"".join(parts)}</svg>')


if __name__ == "__main__":
    import sys

    code = sys.argv[1] if len(sys.argv) > 1 else "9f2b"
    print(f"kod        : {valid_code(code)}")
    for row, value in enumerate(digits(code)):
        marked = [str(w) for w in WEIGHTS if value & w]
        print(f"  rząd {row + 1}  : {' + '.join(marked) or '0':10} = {value:x}")
    print(f"odczyt     : {decode(render(code))}")
    print(f"losowy kod : {random_code()}")
