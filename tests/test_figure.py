"""Bramka poprawności figury: cyfry muszą dać się odczytać Z RYSUNKU.

Nie sprawdzamy tu, czy `svg()` dostał dobre dane — sprawdzamy, czy to, co zostało
narysowane, niesie informację. Test parsuje SVG, znajduje znaczniki szczytów, podstawy
i odstęp kratek, a potem odtwarza hex dokładnie tak, jak zrobiłby to człowiek z ołówkiem:
wysokość = (podstawa − szczyt) / kratka.

Druga bramka jest o druku: kratka musi mieć dość milimetrów, żeby dała się policzyć okiem.
"""

from __future__ import annotations

import collections
import xml.etree.ElementTree as ET

import pytest

from present import codec, figure

NS = "{http://www.w3.org/2000/svg}"
CARD_CONTENT_MM = 210 - 2 * 22  # A4 minus marginesy kartki w templates/karta.html.j2
CARD_HEIGHT_MM = 185  # tyle wolnego miejsca zostaje pod nagłówkiem kartki (max-height w base.css)


TEST_ADDRESS = "komarekzm.github.io/p"  # 21 znaków → 42 cyfry → dwa rzędy po 21


@pytest.fixture(scope="module")
def address() -> str:
    return codec.to_hex(TEST_ADDRESS)


@pytest.fixture(scope="module")
def drawing(address: str) -> ET.Element:
    return ET.fromstring(figure.svg(address))


def _tag(element: ET.Element) -> str:
    return element.tag.replace(NS, "")


def _baselines(root: ET.Element) -> list[float]:
    return [
        float(element.get("y1"))
        for element in root.iter()
        if _tag(element) == "line" and element.get("class") == "baseline"
    ]


def _cell_size(root: ET.Element) -> float:
    """Odstęp poziomych linii siatki w obrębie rzędu — jedna kratka."""
    horizontal = sorted(
        {
            float(element.get("y1"))
            for element in root.iter()
            if _tag(element) == "line"
            and element.get("class") == "grid"
            and element.get("y1") == element.get("y2")
        }
    )
    gaps = [round(b - a, 6) for a, b in zip(horizontal, horizontal[1:]) if b - a > 1e-6]
    if not gaps:
        pytest.fail("w rysunku nie ma siatki poziomej — nie da się policzyć kratek")
    # Najczęstszy odstęp to kratka; pojedyncze większe to przerwy między rzędami.
    cell, _ = collections.Counter(gaps).most_common(1)[0]
    return cell


def _markers(root: ET.Element) -> list[tuple[float, float]]:
    points = []
    for element in root.iter():
        if _tag(element) == "rect" and element.get("class") == "marker":
            x = float(element.get("x")) + float(element.get("width")) / 2
            y = float(element.get("y")) + float(element.get("height")) / 2
            points.append((x, y))
    return points


def test_reading_the_drawing_gives_the_address(drawing: ET.Element, address: str) -> None:
    """Pełny odczyt: szczyt → poziom → cyfra, rząd po rzędzie, kolumna po kolumnie."""
    cell = _cell_size(drawing)
    baselines = sorted(_baselines(drawing))
    assert len(baselines) == 2, "profil ma się łamać na dwa rzędy — inaczej kratki są za małe"

    read = []
    for x, y in sorted(_markers(drawing), key=lambda point: (point[1] > baselines[0], point[0])):
        baseline = min(base for base in baselines if base >= y - 1e-6)
        read.append(round((baseline - y) / cell))

    assert "".join(f"{value:X}" for value in read) == address


def test_every_peak_sits_exactly_on_a_grid_line(drawing: ET.Element) -> None:
    """Połowa kratki byłaby nieczytelna — żaden szczyt nie może wypaść między liniami."""
    cell = _cell_size(drawing)
    baselines = sorted(_baselines(drawing))
    for _, y in _markers(drawing):
        baseline = min(base for base in baselines if base >= y - 1e-6)
        levels = (baseline - y) / cell
        assert abs(levels - round(levels)) < 0.01, f"szczyt wisi między kratkami ({levels:.3f})"


def test_each_column_holds_exactly_one_digit(drawing: ET.Element) -> None:
    """W jednym x może stać tylko jeden szczyt na rząd — nigdy dwie cyfry w tym miejscu."""
    xs = [x for x, _ in _markers(drawing)]
    counts = collections.Counter(xs)
    assert len(counts) == 21, "profil ma 42 znaki w dwóch rzędach po 21 kolumn"
    assert set(counts.values()) == {2}, "każda kolumna musi mieć szczyt w obu rzędach"


def test_cells_are_big_enough_to_count_on_paper(drawing: ET.Element) -> None:
    width_px, height_px = float(drawing.get("width")), float(drawing.get("height"))
    # Przeglądarka skaluje tak, żeby zmieściło się i w szerokości, i w wysokości.
    scale = min(CARD_CONTENT_MM / width_px, CARD_HEIGHT_MM / height_px)
    cell_mm = _cell_size(drawing) * scale
    assert cell_mm >= 4.5, f"kratka ma {cell_mm:.1f} mm — za mało, żeby liczyć bez linijki"


def test_drawing_is_black_and_white(drawing: ET.Element) -> None:
    """Kolor nie może nieść informacji: drukarka czarno-biała musi wystarczyć."""
    colors = {
        value.upper()
        for element in drawing.iter()
        for key, value in element.attrib.items()
        if key in {"fill", "stroke"} and value.startswith("#")
    }
    for color in colors:
        red, green, blue = (int(color[i : i + 2], 16) for i in (1, 3, 5))
        assert max(red, green, blue) - min(red, green, blue) <= 12, f"{color} nie jest szary"
