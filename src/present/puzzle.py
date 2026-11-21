"""Zagadka ze strony: arytmetyka, która daje hasło do kuponu.

Jedno źródło prawdy: hasło wynika Z TYCH LICZB. Zmienisz tabelę albo kwotę —
zmieni się hasło, szyfrogram i to, co trzeba powiedzieć siostrze, gdy utknie.
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
    def remainder(self) -> int:
        """Reszta z dzielenia knutów przez medianę zwycięzcy."""
        return self.total_knuts % self.median_winner.median

    @property
    def answer(self) -> str:
        """Hasło: nazwa domu i reszta, sklejone. Normalizowane po stronie przeglądarki."""
        return f"{self.median_winner.name}{self.remainder}".lower()


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
    if puzzle.remainder == 0:
        raise SystemExit(
            "reszta z dzielenia wyszła 0 — hasło traci cyfrę i robi się zbyt łatwe "
            "do zgadnięcia. Zmień kwotę na pokwitowaniu."
        )
    return puzzle
