"""Bramki siatki 4 × 4: kod musi być do odczytania, a nie do przeczytania.

Testy sprawdzają trzy rzeczy, które łatwo zepsuć po cichu:
1. odczyt z geometrii daje ten sam kod (dla każdej cyfry hex osobno),
2. wagi kolumn naprawdę idą 1 · 2 · 4 · 8 od lewej,
3. kod nie wyciekł jawnym tekstem na kartkę ani na stronę.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from present import box, config

ROOT = Path(__file__).resolve().parent.parent
NS = "{http://www.w3.org/2000/svg}"


@pytest.fixture(scope="module")
def code() -> str:
    return box.valid_code(config.site().address.rsplit("/", 1)[-1])


@pytest.mark.parametrize("digit", list("0123456789abcdef"))
def test_every_digit_survives_the_round_trip(digit: str) -> None:
    value = digit * 4
    assert box.decode(box.render(value)) == value


def test_digits_are_sums_of_marked_weights(code: str) -> None:
    svg = box.render(code)
    root = ET.fromstring(svg)
    dots = [
        (int(e.get("data-row")), int(e.get("data-col")), int(e.get("data-filled")))
        for e in root.iter()
        if e.tag.replace(NS, "") == "circle" and e.get("class") == "dot"
    ]
    assert len(dots) == 16
    sums = [sum(box.WEIGHTS[col] for row, col, filled in dots if row == r and filled) for r in range(4)]
    assert sums == [int(char, 16) for char in code]


def test_weights_go_one_two_four_eight_left_to_right() -> None:
    """Kolejność kolumn jest częścią umowy z kartką — zmiana psuje odczyt."""
    assert box.WEIGHTS == (1, 2, 4, 8)
    root = ET.fromstring(box.render("1111"))
    labels = [
        (float(e.get("x")), e.text)
        for e in root.iter()
        if e.tag.replace(NS, "") == "text" and e.get("class") == "weight"
    ]
    assert [text for _, text in sorted(labels)] == ["1", "2", "4", "8"]


def test_random_code_is_valid_and_not_a_word() -> None:
    for _ in range(20):
        candidate = box.random_code()
        assert re.fullmatch(r"[0-9a-f]{4}", candidate)
        assert candidate not in {"1248", "8421", "c0de", "dead", "beef", "cafe"}


def test_code_does_not_leak_onto_print_or_page(code: str) -> None:
    """Kod ma być w siatce. Napisany obok siatki nie jest już zagadką."""
    for name in ("build/karta-A4.html", "docs/index.html"):
        path = ROOT / name
        if not path.exists():
            pytest.skip(f"brak {name} — uruchom `mise run build`")
        assert code not in path.read_text(encoding="utf-8").lower(), f"{name} zdradza kod"


def test_dots_are_large_enough_to_draw_and_read(code: str) -> None:
    """Kropka co 92 jednostki na SVG; przy A4 daje to ~11 mm rozstawu."""
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
