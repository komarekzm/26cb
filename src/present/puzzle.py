"""Zagadka ze strony: opisy zaklęć bez nazw, z których powstaje słowo.

Reguła: każda notatka opisuje skutek zaklęcia, ale nie podaje jego nazwy. Trzeba
rozpoznać zaklęcie w banku nazw i wziąć jego pierwszą literę. Litery w kolejności
notatek dają słowo — akrostych. Zero liczenia: cała praca to wiedza i skojarzenie.

Bank zaklęć jest podany alfabetycznie, więc litery czytane z banku nie układają hasła —
trzeba dopasować opisy do nazw, żeby trafić w kolejność.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Clue:
    spell: str
    text: str

    @property
    def letter(self) -> str:
        return self.spell[0].upper()


@dataclass(frozen=True)
class Puzzle:
    word: str
    clues: list[Clue]

    @property
    def built_word(self) -> str:
        """Co wychodzi z notatek czytanych po kolei."""
        return "".join(clue.letter for clue in self.clues)

    @property
    def bank(self) -> list[str]:
        """Bank nazw do wyboru — alfabetycznie, żeby nie sugerował kolejności."""
        return sorted((clue.spell for clue in self.clues), key=str.casefold)

    @property
    def bank_word(self) -> str:
        """Co wychodzi, gdy ktoś czyta inicjały wprost z banku, bez dopasowania."""
        return "".join(name[0].upper() for name in self.bank)

    @property
    def answer(self) -> str:
        return self.word.lower()


def load(cfg: dict) -> Puzzle:
    section = cfg["puzzle"]
    clues = [Clue(spell=row["spell"], text=row["text"]) for row in section["clues"]]
    puzzle = Puzzle(word=section["word"], clues=clues)

    if len(clues) != len(puzzle.word):
        raise SystemExit(
            f"notatek jest {len(clues)}, a słowo ma {len(puzzle.word)} liter — "
            "akrostych się nie złoży"
        )
    if puzzle.built_word != puzzle.word:
        raise SystemExit(
            f"pierwsze litery zaklęć dają {puzzle.built_word!r}, a nie {puzzle.word!r}. "
            "Popraw kolejność notatek albo dobór zaklęć."
        )
    if len({clue.spell.casefold() for clue in clues}) != len(clues):
        raise SystemExit("któreś zaklęcie występuje dwa razy — bank przestaje być jednoznaczny")
    if len({clue.text.casefold() for clue in clues}) != len(clues):
        raise SystemExit("dwie notatki mają ten sam tekst — nie da się ich rozróżnić")
    if puzzle.bank_word in (puzzle.word, puzzle.word[::-1]):
        raise SystemExit(
            "bank zaklęć zdradza hasło: czytany po kolei daje to samo słowo. "
            "Zmień zestaw zaklęć."
        )
    for clue in clues:
        if not clue.spell[:1].isalpha():
            raise SystemExit(f"zaklęcie {clue.spell!r} nie zaczyna się od litery")
        if not clue.text.strip():
            raise SystemExit(f"notatka do {clue.spell!r} jest pusta")
    return puzzle
