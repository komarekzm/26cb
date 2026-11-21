"""Zagadka z kartki: arytmetyka, która daje przesunięcie liter w kodzie.

Trzymamy to w jednym miejscu, bo build ma prawo odmówić publikacji, jeśli z danych
w config.toml nie wychodzi sensowne przesunięcie. Liczby na kartce i kod w hexie
muszą opowiadać tę samą historię — inaczej prezent prowadzi donikąd.
"""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean

GALLEON_IN_SICKLES = 17  # kanon: 17 sykli w galeonie
SICKLE_IN_KNUTS = 29  # kanon: 29 knutów w syklu


@dataclass(frozen=True)
class House:
    name: str
    points: list[int]

    @property
    def total(self) -> int:
        return sum(self.points)

    @property
    def average(self) -> float:
        return mean(self.points)

    @property
    def median(self) -> int:
        ordered = sorted(self.points)
        if len(ordered) % 2 == 0:
            raise ValueError(
                f"{self.name}: mediana z parzystej liczby wyników wychodzi ułamkowa — "
                "dodaj albo usuń jedno wydarzenie"
            )
        return ordered[len(ordered) // 2]


@dataclass(frozen=True)
class Puzzle:
    galleons: int
    sickles: int
    knuts: int
    houses: list[House]

    @property
    def total_knuts(self) -> int:
        return (
            self.galleons * GALLEON_IN_SICKLES * SICKLE_IN_KNUTS
            + self.sickles * SICKLE_IN_KNUTS
            + self.knuts
        )

    @property
    def average_winner(self) -> House:
        return max(self.houses, key=lambda house: house.average)

    @property
    def median_winner(self) -> House:
        return max(self.houses, key=lambda house: house.median)

    @property
    def shift(self) -> int:
        """Reszta z dzielenia knutów przez medianę zwycięzcy — tyle liter w tył."""
        return self.total_knuts % self.median_winner.median


def load(cfg: dict) -> Puzzle:
    receipt = cfg["puzzle"]["receipt"]
    points = cfg["puzzle"]["house_points"]
    houses = [House(name=name, points=list(vals)) for name, vals in points["houses"].items()]
    puzzle = Puzzle(
        galleons=receipt["galleons"],
        sickles=receipt["sickles"],
        knuts=receipt["knuts"],
        houses=houses,
    )
    if puzzle.average_winner.name == puzzle.median_winner.name:
        raise SystemExit(
            "zagadka nie ma pointy: średnia i mediana wskazują ten sam dom "
            f"({puzzle.average_winner.name}). Podkręć jedną wartość odstającą."
        )
    if not 1 <= puzzle.shift <= 25:
        raise SystemExit(
            f"przesunięcie wyszło {puzzle.shift} — bezużyteczne. Zmień kwotę na "
            "pokwitowaniu albo medianę zwycięzcy."
        )
    return puzzle
