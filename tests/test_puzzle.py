"""Zagadka musi dawać hasło, które naprawdę otwiera kupon — inaczej to teatr.

Ten plik jest bramką: zmienisz kwotę na pokwitowaniu albo tabelę punktów, a testy
powiedzą, czy hasło, szyfrogram i strona nadal opowiadają tę samą historię.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from present import build, config, puzzle

ROOT = Path(__file__).resolve().parent.parent


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


def test_answer_is_house_and_remainder(loaded: puzzle.Puzzle) -> None:
    expected = f"{loaded.median_winner.name}{loaded.total_knuts % loaded.median_winner.median}"
    assert loaded.answer == expected.lower()
    assert loaded.answer.isalnum()  # normalizacja w przeglądarce nie ma czego gubić


def test_seal_opens_with_the_answer(loaded: puzzle.Puzzle) -> None:
    payload = {"code": "TEST-1", "png": "AAAA", "note": "x"}
    box = build.seal(payload, loaded.answer)
    assert build.open_box(box, loaded.answer) == payload
    assert build.open_box(box, "nieprawdopodobne-haslo") is None


def test_published_page_keeps_secrets_hidden(loaded: puzzle.Puzzle) -> None:
    page = ROOT / "docs" / "index.html"
    if not page.exists():
        pytest.skip("brak docs/index.html — uruchom `mise run build`")
    html = page.read_text(encoding="utf-8")
    coupon = (ROOT / "kupon.txt").read_text(encoding="utf-8").split()[0]
    assert loaded.answer not in html.lower()
    assert coupon not in html
    # Sam schemat data:image jest w skrypcie, ale żadnego gotowego obrazka w HTML-u.
    assert not re.search(r"data:image/png;base64,[A-Za-z0-9+/]{100,}", html)
