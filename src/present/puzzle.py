"""Zagadka ze strony: kwity z apteki eliksirów, z których powstaje hasło.

Reguła: każdy kwit podaje cenę w galeonach, syklach i knutach oraz objętość w dramach.
Trzeba policzyć cenę ZA JEDEN DRAM, ustawić kwity rosnąco i odczytać litery. Kolejność
po cenie łącznej daje inny, błędny ciąg — i to jest cała pułapka zadania.

Wszystko, co build wie o zagadce, pochodzi z config.toml. Jeśli liczby przestaną dawać
słowo albo pułapka przestanie działać, build odmawia publikacji.
"""

from __future__ import annotations

from dataclasses import dataclass

GALLEON_IN_SICKLES = 17  # kanon: 17 sykli w galeonie
SICKLE_IN_KNUTS = 29  # kanon: 29 knutów w syklu
KNUTS_IN_GALLEON = GALLEON_IN_SICKLES * SICKLE_IN_KNUTS  # 493


@dataclass(frozen=True)
class Receipt:
    name: str
    letter: str
    galleons: int
    sickles: int
    knuts: int
    drams: int

    @property
    def total_knuts(self) -> int:
        return (
            self.galleons * KNUTS_IN_GALLEON
            + self.sickles * SICKLE_IN_KNUTS
            + self.knuts
        )

    @property
    def knuts_per_dram(self) -> float:
        return self.total_knuts / self.drams


@dataclass(frozen=True)
class Puzzle:
    word: str
    receipts: list[Receipt]

    @property
    def by_unit_price(self) -> list[Receipt]:
        return sorted(self.receipts, key=lambda receipt: receipt.knuts_per_dram)

    @property
    def by_total_price(self) -> list[Receipt]:
        return sorted(self.receipts, key=lambda receipt: receipt.total_knuts)

    @property
    def built_word(self) -> str:
        return "".join(receipt.letter for receipt in self.by_unit_price)

    @property
    def trap_word(self) -> str:
        """Co wychodzi, gdy ktoś sortuje po cenie łącznej zamiast za dram."""
        return "".join(receipt.letter for receipt in self.by_total_price)

    @property
    def answer(self) -> str:
        return self.word.lower()


def load(cfg: dict) -> Puzzle:
    section = cfg["puzzle"]
    receipts = [
        Receipt(
            name=row["name"],
            letter=row["letter"],
            galleons=row["galleons"],
            sickles=row["sickles"],
            knuts=row["knuts"],
            drams=row["drams"],
        )
        for row in section["receipts"]
    ]
    puzzle = Puzzle(word=section["word"], receipts=receipts)

    if len(receipts) != len(puzzle.word):
        raise SystemExit(
            f"kwitów jest {len(receipts)}, a słowo ma {len(puzzle.word)} liter — "
            "zagadka nie ułoży się w całość"
        )
    if puzzle.built_word != puzzle.word:
        raise SystemExit(
            f"sortowanie po cenie za dram daje {puzzle.built_word!r}, a nie {puzzle.word!r}. "
            "Popraw litery albo kwoty."
        )
    if puzzle.trap_word == puzzle.word:
        raise SystemExit(
            "sortowanie po cenie łącznej daje to samo słowo — pułapka nie działa, "
            "a wtedy zadanie rozwiązuje się bez liczenia ceny za dram"
        )
    if any(receipt.drams <= 0 for receipt in receipts):
        raise SystemExit("każdy kwit musi mieć dodatnią objętość w dramach")
    if any(receipt.knuts_per_dram != int(receipt.knuts_per_dram) for receipt in receipts):
        raise SystemExit(
            "cena za dram wychodzi ułamkowa — hasło ma być do policzenia w głowie, "
            "bez kalkulatora i zaokrągleń"
        )
    return puzzle
