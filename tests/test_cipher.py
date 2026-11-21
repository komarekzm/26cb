"""Szyfr liczbowy: litera = numer w alfabecie, kropka i ukośnik bez zmian."""

from __future__ import annotations

from pathlib import Path

import pytest

from present import cipher, config

ROOT = Path(__file__).resolve().parent.parent


def test_numbers_start_at_one() -> None:
    """Legenda ma być ta jedna, znana: a = 1, b = 2, … z = 26."""
    assert cipher.number("a") == 1
    assert cipher.number("b") == 2
    assert cipher.number("z") == 26
    assert cipher.letter(1) == "a"
    assert cipher.letter(26) == "z"


def test_whole_address_round_trips() -> None:
    address = config.site().address
    tokens = cipher.encode(address)
    assert cipher.decode(tokens) == address


def test_punctuation_is_left_alone() -> None:
    tokens = cipher.encode("ab.c/d")
    assert tokens == ["1", "2", ".", "3", "/", "4"]
    assert cipher.decode(tokens) == "ab.c/d"


def test_no_number_exceeds_the_alphabet() -> None:
    """Właśnie po to zmieniliśmy hex: żadnej cyfry ponad 26 i żadnego a–f."""
    for token in cipher.encode(config.site().address):
        if token.isdigit():
            assert 1 <= int(token) <= 26


def test_unknown_sign_is_rejected() -> None:
    with pytest.raises(ValueError):
        cipher.decode(["1", "?", "2"])
    with pytest.raises(ValueError):
        cipher.encode("zażółć")  # polskie znaki nie mieszczą się w legendzie


def test_card_does_not_spell_the_address_out() -> None:
    """Na kartce ma być zapis liczbowy, nie gotowy adres."""
    card = ROOT / "build" / "karta-A4.html"
    if not card.exists():
        pytest.skip("brak build/karta-A4.html — uruchom `mise run build`")
    html = card.read_text(encoding="utf-8")
    assert config.site().address not in html
    assert "komarekzm" not in html  # sama domena już zdradza połowę


def test_rows_wrap_the_whole_strip() -> None:
    tokens = cipher.encode(config.site().address)
    rows = cipher.rows(tokens, per_row=7)
    assert sum(len(row) for row in rows) == len(tokens)
    assert all(len(row) <= 7 for row in rows)
