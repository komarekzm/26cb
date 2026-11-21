"""Bramki siatki 4 × 5: numer litery w alfabecie musi dać się odczytać z rysunku.

Kod to cztery małe litery. Siatka niesie ich numery (1 = a … 26 = z), a wagi kolumn
(1, 2, 4, 8, 16) pozwalają zapisać każdą liczbę do 31 — czyli cały alfabet.

Testy pilnują tego, co psuje się po cichu: odczytu z geometrii, kolejności wag,
braku wycieku kodu i tego, że kropki da się postawić ołówkiem.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from present import box

ROOT = Path(__file__).resolve().parent.parent
NS = "{http://www.w3.org/2000/svg}"


# Siatka 4 × 5 nie jest już na kartce (zastąpił ją zapis liczbowy), ale zostaje
# w projekcie jako alternatywa — testy nie mogą więc zależeć od aktualnego adresu.
TEST_CODE = "hvqm"


@pytest.fixture(scope="module")
def code() -> str:
    return box.valid_code(TEST_CODE)


@pytest.mark.parametrize("letter", list(box.LETTERS))
def test_every_letter_survives_the_round_trip(letter: str) -> None:
    value = letter * 4
    assert box.decode(box.render(value)) == value


def test_letters_are_numbered_from_one(code: str) -> None:
    """Legenda ma być dosłowna: a = 1, b = 2, … z = 26."""
    assert box.digits("abcd") == [1, 2, 3, 4]
    assert box.digits("zzzz") == [26, 26, 26, 26]
    assert box.digits(code) == [box.LETTERS.index(char) + 1 for char in code]


def test_row_sums_are_the_letter_numbers(code: str) -> None:
    root = ET.fromstring(box.render(code))
    dots = [
        (int(e.get("data-row")), int(e.get("data-col")), int(e.get("data-filled")))
        for e in root.iter()
        if e.tag.replace(NS, "") == "circle" and e.get("class") == "dot"
    ]
    assert len(dots) == 20, "cztery rzędy po pięć kolumn"
    sums = [sum(box.WEIGHTS[col] for row, col, filled in dots if row == r and filled) for r in range(4)]
    assert sums == box.digits(code)


def test_weights_go_one_to_sixteen_left_to_right() -> None:
    """Pięć kolumn, bo alfabet sięga 26 — cztery kolumny kończą się na 15."""
    assert box.WEIGHTS == (1, 2, 4, 8, 16)
    root = ET.fromstring(box.render("aaaa"))
    labels = [
        (float(e.get("x")), e.text)
        for e in root.iter()
        if e.tag.replace(NS, "") == "text" and e.get("class") == "weight"
    ]
    assert [text for _, text in sorted(labels)] == ["1", "2", "4", "8", "16"]


def test_random_code_is_four_letters_and_not_a_word() -> None:
    for _ in range(20):
        candidate = box.random_code()
        assert re.fullmatch(r"[a-z]{4}", candidate)
        assert candidate not in {"test", "abcd", "deko", "kota"}


def test_code_does_not_leak_onto_print_or_page(code: str) -> None:
    """Kod ma być w siatce. Napisany obok siatki nie jest już zagadką."""
    for name in ("build/karta-A4.html", "docs/index.html"):
        path = ROOT / name
        if not path.exists():
            pytest.skip(f"brak {name} — uruchom `mise run build`")
        assert code not in path.read_text(encoding="utf-8").lower(), f"{name} zdradza kod"


def test_dots_are_large_enough_to_draw_and_read(code: str) -> None:
    root = ET.fromstring(box.render(code))
    xs = sorted(
        float(e.get("cx"))
        for e in root.iter()
        if e.tag.replace(NS, "") == "circle" and e.get("class") == "dot"
    )
    spacing = min(b - a for a, b in zip(xs, xs[1:]) if b - a > 0)
    width = float(root.get("width"))
    spacing_mm = spacing * 166 / width  # 166 mm to szerokość zadruku kartki
    assert spacing_mm >= 9, f"kropki co {spacing_mm:.1f} mm — za gęsto do rysowania ręką"


def test_out_of_alphabet_sum_is_rejected() -> None:
    """Suma 31 (wszystkie kolumny) nie jest literą — dekoder musi to zgłosić."""
    svg = box.render("zzzz").replace('data-filled="0"', 'data-filled="1"')
    with pytest.raises(ValueError):
        box.decode(svg)
