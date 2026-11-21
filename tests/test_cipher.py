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


def test_numbers_are_written_in_hex() -> None:
    """Numer litery w hexie: 10 = A, 15 = F, 16 = 10, 26 = 1A."""
    assert cipher.symbol(9) == "9"
    assert cipher.symbol(10) == "A"
    assert cipher.symbol(15) == "F"
    assert cipher.symbol(16) == "10"
    assert cipher.symbol(17) == "11"
    assert cipher.symbol(26) == "1A"
    assert cipher.value_of("A") == 10
    assert cipher.value_of("1A") == 26
    assert cipher.decode(["B"] * 2) == "kk"  # B = 11 = k


def domain_and_code() -> tuple[str, str]:
    domain, _, code = config.site().address.rpartition("/")
    return domain + "/", code


def test_domain_round_trips_and_grid_carries_the_code() -> None:
    """Pasek = domena, siatka = kod. Razem muszą dać dokładnie adres."""
    from present import box

    domain, code = domain_and_code()
    tokens = cipher.encode(domain)
    assert cipher.decode(tokens) == domain
    assert box.decode_hex(box.render_hex(code, weights=(1, 2, 4, 8))) == code
    assert cipher.decode(tokens) + code == config.site().address


def test_punctuation_is_left_alone() -> None:
    tokens = cipher.encode("ab.c/d")
    assert tokens == ["1", "2", ".", "3", "/", "4"]
    assert cipher.decode(tokens) == "ab.c/d"


def test_digit_in_domain_is_rejected_with_a_reason() -> None:
    """Cyfra w domenie myliłaby się z zapisem hex — kod ma swoje miejsce w siatce."""
    with pytest.raises(ValueError, match="siatka"):
        cipher.encode("komarekzm2.github.io/")


def test_tokens_stay_within_hex_digits() -> None:
    """Żadnych liter spoza A–F: po F liczenie idzie dalej jako 10, 11, … 1A."""
    for token in cipher.encode(domain_and_code()[0]):
        assert token in ". /".split() or __import__("re").fullmatch(r"[0-9A-F]{1,2}", token), token


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
    tokens = cipher.encode(domain_and_code()[0])
    rows = cipher.rows(tokens, per_row=7)
    assert sum(len(row) for row in rows) == len(tokens)
    assert all(len(row) <= 7 for row in rows)
