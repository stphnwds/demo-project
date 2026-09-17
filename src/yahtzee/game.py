"""Turn and match orchestration, independent of any user interface."""

import random
from dataclasses import dataclass, field
from typing import Sequence

from src.yahtzee.dice import DiceCup
from src.yahtzee.scoring import CATEGORIES, ScoreCard


@dataclass
class Player:
    name: str
    card: ScoreCard = field(default_factory=ScoreCard)

    @property
    def total(self) -> int:
        return self.card.total


class Game:
    """A match of thirteen rounds for one or more players."""

    def __init__(self, names: Sequence[str], rng: random.Random | None = None) -> None:
        if not names:
            raise ValueError("A game needs at least one player")

        self.rng = rng or random.Random()
        self.players = [Player(name) for name in names]
        self.cup = DiceCup(self.rng)
        self.rounds = len(CATEGORIES)

    @property
    def is_over(self) -> bool:
        return all(p.card.is_complete for p in self.players)

    def start_turn(self) -> list[int]:
        """Clear the dice and make the first of the turn's three rolls."""
        self.cup.reset()
        return self.cup.roll()

    def reroll(self, keep: set[int]) -> list[int]:
        return self.cup.roll(keep)

    def take_category(self, player: Player, key: str) -> int:
        return player.card.record(key, self.cup.dice)

    def standings(self) -> list[Player]:
        """Players ranked best-first."""
        return sorted(self.players, key=lambda p: p.total, reverse=True)

    def winners(self) -> list[Player]:
        """Every player tied for the highest total."""
        best = max(p.total for p in self.players)
        return [p for p in self.players if p.total == best]
