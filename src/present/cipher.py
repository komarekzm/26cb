"""Szyfr liczbowy: adres zapisany numerami liter, bez hexa i bez binarki.

Legenda jest ta jedna, którą każdy zna: a = 1, b = 2, … z = 26. Kropki i ukośnik
zostają sobą, bo w adresie są jednoznaczne — dzięki temu nie trzeba wymyślać numerów
dla znaków specjalnych.

Dla `komarekzm.github.io/p` daje to 21 znaków:

    11 15 13 1 18 5 11 26 13 . 7 9 20 8 21 2 . 9 15 / 16

Zaleta nad hexem: żadnej cyfry powyżej 26 i żadnej litery a–f do rozszyfrowania.
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


def encode(address: str) -> list[str]:
    """Adres → lista znaków zapisu: liczby jako tekst, interpunkcja bez zmian."""
    tokens: list[str] = []
    for char in address:
        if char.isalpha():
            tokens.append(str(number(char)))
        elif char in PUNCTUATION:
            tokens.append(char)
        else:
            raise ValueError(f"znak {char!r} nie ma miejsca w tej legendzie")
    return tokens


def decode(tokens: list[str]) -> str:
    """Lista znaków zapisu → adres. Musi wrócić dokładnie to samo."""
    out: list[str] = []
    for token in tokens:
        if token in PUNCTUATION:
            out.append(token)
        elif re.fullmatch(r"\d{1,2}", token):
            out.append(letter(int(token)))
        else:
            raise ValueError(f"nieznany znak zapisu: {token!r}")
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
    print(f"odczyt : {decode(tokens)}  (zgodny: {decode(tokens) == address})")
