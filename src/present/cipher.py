"""Szyfr liczbowy: adres zapisany numerami liter, bez hexa i bez binarki.

Legenda jest ta jedna, którą każdy zna: a = 1, b = 2, … z = 26. Kropki i ukośnik
zostają sobą, bo w adresie są jednoznaczne — dzięki temu nie trzeba wymyślać numerów
dla znaków specjalnych.

Dla `komarekzm.github.io/p` daje to 21 znaków:

    11 15 13 1 18 5 11 26 13 . 7 9 20 8 21 2 . 9 15 / 16

Zapis wartości idzie jak w hexie: 1–9 to cyfry, a od dziesiątki wchodzą litery
(10 = A, 11 = B, … 26 = Q). Dzięki temu jeden znak adresu to jeden znak zapisu —
bez dwucyfrowych liczb, które mylą się przy przepisywaniu.

    B F D 1 I 5 B Q D . 7 9 K 8 L 2 . 9 F / G
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
    """Numer litery → znak zapisu: 1–9 cyfra, 10–26 wielka litera (10 = A)."""
    if not 1 <= value <= len(LETTERS):
        raise ValueError(f"numer {value} nie jest literą alfabetu (1–26)")
    if value <= 9:
        return str(value)
    return chr(ord("A") + value - 10)


def value_of(token: str) -> int:
    """Znak zapisu → numer litery."""
    if len(token) == 1 and token.isdigit() and token != "0":
        return int(token)
    if len(token) == 1 and "A" <= token <= "Q":
        return 10 + ord(token) - ord("A")
    raise ValueError(f"nieznany znak zapisu: {token!r}")


def encode(address: str) -> list[str]:
    """Adres → lista znaków zapisu: liczby jako tekst, interpunkcja bez zmian."""
    tokens: list[str] = []
    for char in address:
        if char.isalpha():
            tokens.append(symbol(number(char)))
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
    print("legenda: " + "  ".join(f"{symbol(v)}={cipher_letter}" for v, cipher_letter in enumerate(LETTERS, start=1) if v in (1, 5, 9, 10, 11, 15, 20, 26)))
    print(f"odczyt : {decode(tokens)}  (zgodny: {decode(tokens) == address})")
