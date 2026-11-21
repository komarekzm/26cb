"""Zagadka musi prowadzić do słowa, a słowo musi otwierać wiadomość.

Bramki: inicjały zaklęć w kolejności notatek dają hasło; bank zaklęć (alfabetyczny)
go nie zdradza; żadne zaklęcie ani żadna notatka się nie powtarza; hasła nie ma
w opublikowanym HTML-u; a całe rozwiązanie da się odtworzyć z samej strony.
"""

from __future__ import annotations

import collections
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


def _page() -> str:
    page = ROOT / "docs" / "index.html"
    if not page.exists():
        pytest.skip("brak docs/index.html — uruchom `mise run build`")
    return page.read_text(encoding="utf-8")


def test_initials_spell_the_word(loaded: puzzle.Puzzle) -> None:
    """To jest rozwiązanie: pierwsze litery rozpoznanych zaklęć, w kolejności notatek."""
    assert loaded.built_word == loaded.word


def test_letter_count_matches_the_word(loaded: puzzle.Puzzle) -> None:
    assert collections.Counter(clue.letter for clue in loaded.clues) == collections.Counter(
        loaded.word
    )


def test_bank_does_not_give_the_answer_away(loaded: puzzle.Puzzle) -> None:
    """Bank jest alfabetyczny: czytany po kolei musi dawać coś innego niż hasło."""
    assert loaded.bank_word != loaded.word
    assert loaded.bank_word != loaded.word[::-1]


def test_bank_is_sorted_and_complete(loaded: puzzle.Puzzle) -> None:
    assert loaded.bank == sorted(loaded.bank, key=str.casefold)
    assert len(loaded.bank) == len(loaded.clues)


def test_every_spell_and_note_is_unique(loaded: puzzle.Puzzle) -> None:
    assert len({clue.spell for clue in loaded.clues}) == len(loaded.clues)
    assert len({clue.text for clue in loaded.clues}) == len(loaded.clues)


def test_no_arithmetic_is_needed(loaded: puzzle.Puzzle) -> None:
    """Zagadka ma być o wiedzy, nie o liczeniu: żadnych kwot ani objętości w treści."""
    for clue in loaded.clues:
        assert not re.search(r"\d", clue.text), clue.text


def test_message_opens_with_the_word(loaded: puzzle.Puzzle) -> None:
    payload = {"text": "pod monitorem"}
    box = build.seal(payload, loaded.answer)
    assert build.open_box(box, loaded.answer) == payload
    assert build.open_box(box, "nieprawdopodobne-haslo") is None


def test_published_page_keeps_secrets_hidden(loaded: puzzle.Puzzle) -> None:
    html = _page()
    coupon = (ROOT / "kupon.txt").read_text(encoding="utf-8").split()[0]
    assert loaded.answer not in html.lower()
    assert coupon not in html
    assert not re.search(r"data:image/png;base64,[A-Za-z0-9+/]{100,}", html)


def test_word_can_be_rebuilt_from_the_published_page(loaded: puzzle.Puzzle, cfg: dict) -> None:
    """Najmocniejsza bramka: bierzemy notatki i bank z HTML-a, nie z modelu.

    Dopasowanie notatka → zaklęcie bierzemy z configu (to jest „wiedza”), ale kolejność
    notatek, ich treść i zawartość banku czytamy z opublikowanej strony.
    """
    html = _page()
    notes = re.findall(r'<span class="clue">([^<]+)</span>', html)
    bank = re.findall(r"<li>([^<]+)</li>", html)

    assert len(notes) == 9, f"na stronie jest {len(notes)} notatek"
    assert len(bank) == 9, f"w banku jest {len(bank)} zaklęć"

    expected_order = [row["text"] for row in cfg["puzzle"]["clues"]]
    assert notes == expected_order, "kolejność notatek na stronie nie zgadza się z configiem"

    lookup = {row["text"]: row["spell"] for row in cfg["puzzle"]["clues"]}
    built = ""
    for note in notes:
        spell = lookup[note]
        assert spell in bank, f"{spell!r} nie ma w banku na stronie"
        built += spell[0].upper()

    assert built == "ALOHOMORA", f"ze strony wychodzi {built!r}"
