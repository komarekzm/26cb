"""Kodek: adres strony <-> hex i bity, plus układ wierszy na kartkę do druku.

Hex jest domyślny, bo do ręcznego dekodowania jest czterokrotnie krótszy od bitów
(dwa znaki na literę zamiast ośmiu). Bity zostają jako wariant — czasem ktoś woli
trudniejszą drogę, a kod i tak musi się zgadzać.
"""

from __future__ import annotations

import sys

BYTES_PER_ROW = 8  # 16 znaków hex w wierszu — mieści się na A4 dużym stopniem


def to_hex(text: str) -> str:
    return text.encode("utf-8").hex().upper()


def to_binary(text: str) -> str:
    return " ".join(f"{byte:08b}" for byte in text.encode("utf-8"))


def from_hex(code: str) -> str:
    cleaned = "".join(code.split()).replace("0x", "").replace(",", "")
    if len(cleaned) % 2:
        raise ValueError("hex musi mieć parzystą liczbę znaków — dwa znaki to jedna litera")
    return bytes.fromhex(cleaned).decode("utf-8")


def from_binary(code: str) -> str:
    return bytes(int(chunk, 2) for chunk in code.split()).decode("utf-8")


def hex_rows(text: str, per_row: int = BYTES_PER_ROW) -> list[str]:
    """Wiersze po `per_row` bajtów, każdy bajt jako para znaków — do druku."""
    code = to_hex(text)
    pairs = [code[i : i + 2] for i in range(0, len(code), 2)]
    return [" ".join(pairs[i : i + per_row]) for i in range(0, len(pairs), per_row)]


def ascii_table(start: int = 0x20, end: int = 0x7E) -> list[tuple[str, str]]:
    """Pary (hex, znak) dla drukowalnego ASCII — klucz do dekodowania na piechotę."""
    glyphs = {0x20: "␣"}
    return [(f"{code:02X}", glyphs.get(code, chr(code))) for code in range(start, end + 1)]


if __name__ == "__main__":
    from present.config import site

    if len(sys.argv) > 1 and sys.argv[1] == "decode":
        raw = " ".join(sys.argv[2:])
        if not raw and sys.stdin.isatty():
            # Bez argumentu i bez potoku: sprawdź samego siebie na adresie z configu.
            raw = to_hex(site().address)
            print(f"brak argumentu — sprawdzam siebie: {raw}")
        elif not raw:
            raw = sys.stdin.read()
        print(from_hex(raw))
    else:
        address = site().address
        print(f"adres : {address}")
        print(f"hex   : {to_hex(address)}")
        for row in hex_rows(address):
            print(f"        {row}")
        print(f"bity  : {to_binary(address)}")
