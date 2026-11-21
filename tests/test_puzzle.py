"""Zagadka na kartce musi dawać dokładnie to przesunięcie, które odszyfrowuje kod.

Ten plik jest bramką: jeśli ktoś zmieni kwotę na pokwitowaniu albo tabelę punktów,
testy powiedzą, czy kod z kartki nadal prowadzi do adresu.
"""

from __future__ import annotations

import pytest

from present import codec, config, puzzle


@pytest.fixture(scope="module")
def cfg() -> dict:
    return config.load()


@pytest.fixture(scope="module")
def loaded(cfg: dict) -> puzzle.Puzzle:
    return puzzle.load(cfg)


def test_receipt_counts_knuts(loaded: puzzle.Puzzle, cfg: dict) -> None:
    # 1 galeon = 17 sykli, 1 sykiel = 29 knutów → galeon to 493 knuty.
    receipt = cfg["puzzle"]["receipt"]
    expected = receipt["galleons"] * 493 + receipt["sickles"] * 29 + receipt["knuts"]
    assert loaded.total_knuts == expected


def test_average_and_median_disagree(loaded: puzzle.Puzzle) -> None:
    # Bez tego zagadka nie ma pointy — build też tego pilnuje.
    assert loaded.average_winner.name != loaded.median_winner.name


def test_median_is_the_middle_value(loaded: puzzle.Puzzle) -> None:
    for house in loaded.houses:
        ordered = sorted(house.points)
        assert house.median == ordered[len(ordered) // 2]


def test_shift_is_usable(loaded: puzzle.Puzzle) -> None:
    assert 1 <= loaded.shift <= 25


def test_card_code_leads_back_to_address(loaded: puzzle.Puzzle) -> None:
    address = config.site().address
    on_card = codec.caesar(address, loaded.shift)  # to jest drukowane jako hex
    decoded = codec.from_hex(codec.to_hex(on_card))
    assert codec.caesar(decoded, -loaded.shift) == address


def test_caesar_roundtrip() -> None:
    text = "komarekzm.github.io/p"
    assert codec.caesar(codec.caesar(text, 7), -7) == text


def test_caesar_leaves_punctuation_alone() -> None:
    # Kropki i ukośnik nie mogą się przesuwać, inaczej adres przestaje być adresem.
    assert codec.caesar("2.2/9", 5) == "2.2/9"
    assert codec.caesar("a.b/c", 1) == "b.c/d"
