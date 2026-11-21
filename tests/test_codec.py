"""Kodek musi być odwracalny — inaczej kartka prowadzi donikąd."""

from __future__ import annotations

import pytest

from present import codec


def test_hex_roundtrip() -> None:
    address = "komarekzm.github.io/p"
    assert codec.from_hex(codec.to_hex(address)) == address


def test_binary_roundtrip() -> None:
    address = "komarekzm.github.io/p"
    assert codec.from_binary(codec.to_binary(address)) == address


def test_hex_is_uppercase_pairs() -> None:
    # Kartka jest drukowana, więc mieszanie wielkości liter tylko myli.
    assert codec.to_hex("k") == "6B"


def test_rows_keep_every_byte() -> None:
    address = "komarekzm.github.io/p"
    rows = codec.hex_rows(address, per_row=8)
    rebuilt = "".join(rows).replace(" ", "")
    assert codec.from_hex(rebuilt) == address
    assert len(rows) == 3  # 21 znaków adresu po 8 bajtów w wierszu


def test_odd_hex_is_rejected() -> None:
    # Niedokończona para to najczęstszy błąd przy przepisywaniu z kartki.
    with pytest.raises(ValueError):
        codec.from_hex("6B 6")


def test_ascii_table_covers_key_characters() -> None:
    table = dict(codec.ascii_table())
    assert table["2E"] == "."  # kropka w domenie
    assert table["2F"] == "/"  # ukośnik przed ścieżką
    assert table["20"] == "␣"  # spacja pokazana jako znak, nie jako puste pole
