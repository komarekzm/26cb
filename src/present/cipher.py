"""Szyfr liczbowy: adres zapisany numerami liter, bez hexa i bez binarki.

Legenda jest ta jedna, którą każdy zna: a = 1, b = 2, … z = 26. Kropki i ukośnik
zostają sobą, bo w adresie są jednoznaczne — dzięki temu nie trzeba wymyślać numerów
dla znaków specjalnych.

Dla `komarekzm.github.io/p` daje to 21 znaków:

    11 15 13 1 18 5 11 26 13 . 7 9 20 8 21 2 . 9 15 / 16

Numer litery zapisujemy w hexie: 1–9 to cyfry, 10 = A, 11 = B, 12 = C, 13 = D,
14 = E, 15 = F, a potem liczenie idzie dalej — 16 = 10, 17 = 11, … 26 = 1A.

    B F D 1 12 5 B 1A D . 7 9 14 8 15 2 . 9 F / 10
"""

from __future__ import annotations

import re

LETTERS = "abcdefghijklmnopqrstuvwxyz"
PUNCTUATION = "./-_"  # znaki, które zostają w zapisie bez zmian
PER_ROW = 7  # ile znaków w wierszu na kartce


def number(letter: str) -> int:
    """Litera → numer w alfabecie (a = 1)."""
    try:
        return LETTERS.index(letter.lower()) + 1
    except ValueError:
        raise ValueError(f"nie ma takiej litery w alfabecie: {letter!r}") from None


def letter(value: int) -> str:
    """Numer → litera (1 = a)."""
    if not 1 <= value <= len(LETTERS):
        raise ValueError(f"numer {value} nie jest literą alfabetu (1–26)")
    return LETTERS[value - 1]


def symbol(value: int) -> str:
    """Numer litery → zapis szesnastkowy: 1–9 cyfra, 10 = A … 15 = F, 16 = 10, 26 = 1A."""
    if not 1 <= value <= len(LETTERS):
        raise ValueError(f"numer {value} nie jest literą alfabetu (1–26)")
    return f"{value:X}"


def value_of(token: str) -> int:
    """Zapis szesnastkowy → numer litery."""
    if not re.fullmatch(r"[0-9A-F]{1,2}", token):
        raise ValueError(f"nieznany znak zapisu: {token!r}")
    value = int(token, 16)
    if not 1 <= value <= len(LETTERS):
        raise ValueError(f"zapis {token!r} leży poza alfabetem (1–26)")
    return value


def encode(address: str) -> list[str]:
    """Adres → lista znaków zapisu: liczby jako tekst, interpunkcja bez zmian."""
    tokens: list[str] = []
    for char in address:
        if char.isalpha():
            tokens.append(symbol(number(char)))
        elif char in PUNCTUATION:
            tokens.append(char)
        elif char.isdigit():
            raise ValueError(
                f"cyfra {char!r} nie należy do domeny — kod adresu niesie siatka, nie pasek"
            )
        else:
            raise ValueError(f"znak {char!r} nie ma miejsca w tej legendzie")
    return tokens


def decode(tokens: list[str]) -> str:
    """Lista znaków zapisu → adres. Musi wrócić dokładnie to samo."""
    out: list[str] = []
    for token in tokens:
        if token in PUNCTUATION:
            out.append(token)
        else:
            out.append(letter(value_of(token)))
    return "".join(out)


def rows(tokens: list[str], per_row: int = PER_ROW) -> list[list[str]]:
    return [tokens[i : i + per_row] for i in range(0, len(tokens), per_row)]


if __name__ == "__main__":
    import sys

    address = sys.argv[1] if len(sys.argv) > 1 else "komarekzm.github.io/p"
    tokens = encode(address)
    print(f"adres  : {address}")
    print(f"znaków : {len(tokens)}")
    for row in rows(tokens):
        print("        " + " ".join(f"{token:>2}" for token in row))
    print("legenda: " + "  ".join(f"{symbol(v)}={ch}" for v, ch in enumerate(LETTERS, start=1)))
    print(f"odczyt : {decode(tokens)}  (zgodny: {decode(tokens) == address})")
