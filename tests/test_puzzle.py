"""Zagadka musi prowadzić do słowa, a słowo musi otwierać wiadomość.

Ten plik jest bramką: zmienisz kwoty, litery albo objętości, a testy powiedzą, czy
wychodzi słowo z configu, czy pułapka z ceną łączną nadal daje inny ciąg, i czy
opublikowana strona nie zdradza hasła.
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


def test_prices_convert_to_knuts(loaded: puzzle.Puzzle) -> None:
    # Kanon: 1 galeon = 17 sykli, 1 sykiel = 29 knutów → galeon to 493 knuty.
    for receipt in loaded.receipts:
        expected = receipt.galleons * 493 + receipt.sickles * 29 + receipt.knuts
        assert receipt.total_knuts == expected, receipt.name


def test_unit_price_is_a_whole_number(loaded: puzzle.Puzzle) -> None:
    """Hasło ma być do policzenia w głowie — ułamki i zaokrąglenia psują zadanie."""
    for receipt in loaded.receipts:
        assert receipt.knuts_per_dram == int(receipt.knuts_per_dram), receipt.name


def test_letters_are_exactly_the_word(loaded: puzzle.Puzzle) -> None:
    assert collections.Counter(r.letter for r in loaded.receipts) == collections.Counter(
        loaded.word
    )


def test_sorting_by_unit_price_builds_the_word(loaded: puzzle.Puzzle) -> None:
    """To jest rozwiązanie zagadki — kolejność po cenie za dram."""
    assert loaded.built_word == loaded.word


def test_sorting_by_total_price_gives_a_different_word(loaded: puzzle.Puzzle) -> None:
    """Pułapka musi działać, inaczej zadanie rozwiązuje się bez ceny za dram."""
    assert loaded.trap_word != loaded.word
    assert loaded.trap_word != loaded.built_word


def test_answer_is_the_lowercase_word(loaded: puzzle.Puzzle) -> None:
    assert loaded.answer == loaded.word.lower()
    assert loaded.answer.isalpha()


def test_message_opens_with_the_word(loaded: puzzle.Puzzle) -> None:
    payload = {"text": "pod monitorem"}
    box = build.seal(payload, loaded.answer)
    assert build.open_box(box, loaded.answer) == payload
    assert build.open_box(box, loaded.trap_word.lower()) is None  # błędne słowo nie przechodzi
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


def test_answer_is_not_readable_straight_down_the_table(loaded: puzzle.Puzzle) -> None:
    """Litery w kolejności z configu = kolejność na stronie. Nie mogą składać hasła."""
    displayed = "".join(receipt.letter for receipt in loaded.receipts)
    assert displayed != loaded.word, "hasło czyta się wprost z tabeli, bez liczenia"
    assert displayed != loaded.word[::-1], "hasło czyta się z tabeli od dołu"
    assert displayed != loaded.trap_word


@pytest.mark.parametrize(
    "key",
    [
        lambda receipt: receipt.drams,
        lambda receipt: receipt.name,
        lambda receipt: receipt.total_knuts,
        lambda receipt: receipt.galleons,
        lambda receipt: receipt.sickles,
    ],
    ids=["dramy", "nazwa", "suma", "galeony", "sykle"],
)
def test_no_simple_sort_spells_the_answer(loaded: puzzle.Puzzle, key) -> None:
    """Każde sortowanie „na oko” musi dawać inny ciąg niż hasło."""
    assert "".join(r.letter for r in sorted(loaded.receipts, key=key)) != loaded.word


def test_the_word_can_be_rebuilt_from_the_published_page_alone() -> None:
    """Najmocniejsza bramka: rozwiązanie odtwarzamy z HTML-u, nie z modelu.

    Parsujemy tabelę tak, jak widzi ją człowiek: litera, dramy, cena w g/s/k.
    Potem liczymy knuty, dzielimy przez dramy i układamy słowo.
    """
    page = ROOT / "docs" / "index.html"
    if not page.exists():
        pytest.skip("brak docs/index.html — uruchom `mise run build`")
    html = page.read_text(encoding="utf-8")

    rows = re.findall(
        r'<td class="stamp">(\w)</td>.*?<td>(\d+)</td>\s*<td>(\d+)g (\d+)s (\d+)k</td>',
        html,
        re.S,
    )
    assert len(rows) == 9, f"w tabeli jest {len(rows)} kwitów, a powinno być 9"

    priced = []
    for letter, drams, g, s, k in rows:
        knuts = int(g) * 493 + int(s) * 29 + int(k)
        unit = knuts / int(drams)
        assert unit == int(unit), f"{letter}: cena za dram nie jest liczbą całkowitą"
        priced.append((unit, letter))

    built = "".join(letter for _, letter in sorted(priced))
    assert built == "ALOHOMORA", f"z tabeli wychodzi {built!r}"
