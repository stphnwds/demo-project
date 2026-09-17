"""Scoring rules for the thirteen Yahtzee categories."""

from collections import Counter
from dataclasses import dataclass, field
from typing import Callable, Sequence

UPPER_BONUS_THRESHOLD = 63
UPPER_BONUS = 35


def _sum_of(face: int) -> Callable[[Sequence[int]], int]:
    """Upper section: total of all dice showing `face`."""

    def score(dice: Sequence[int]) -> int:
        return sum(d for d in dice if d == face)

    return score


def _n_of_a_kind(n: int) -> Callable[[Sequence[int]], int]:
    """Total of all dice, but only if some face appears at least `n` times."""

    def score(dice: Sequence[int]) -> int:
        counts = Counter(dice)
        return sum(dice) if any(c >= n for c in counts.values()) else 0

    return score


def _full_house(dice: Sequence[int]) -> int:
    counts = sorted(Counter(dice).values())
    return 25 if counts == [2, 3] else 0


def _straight(length: int, points: int) -> Callable[[Sequence[int]], int]:
    """Points if the dice contain `length` consecutive distinct faces."""

    def score(dice: Sequence[int]) -> int:
        faces = sorted(set(dice))
        run = 1
        longest = 1
        for prev, cur in zip(faces, faces[1:]):
            run = run + 1 if cur == prev + 1 else 1
            longest = max(longest, run)
        return points if longest >= length else 0

    return score


def _yahtzee(dice: Sequence[int]) -> int:
    return 50 if len(set(dice)) == 1 else 0


@dataclass(frozen=True)
class Category:
    """One line on the score card."""

    key: str
    label: str
    scorer: Callable[[Sequence[int]], int]
    upper: bool = False

    def score(self, dice: Sequence[int]) -> int:
        return self.scorer(dice)


CATEGORIES: tuple[Category, ...] = (
    Category("ones", "Ones", _sum_of(1), upper=True),
    Category("twos", "Twos", _sum_of(2), upper=True),
    Category("threes", "Threes", _sum_of(3), upper=True),
    Category("fours", "Fours", _sum_of(4), upper=True),
    Category("fives", "Fives", _sum_of(5), upper=True),
    Category("sixes", "Sixes", _sum_of(6), upper=True),
    Category("three_of_a_kind", "Three of a Kind", _n_of_a_kind(3)),
    Category("four_of_a_kind", "Four of a Kind", _n_of_a_kind(4)),
    Category("full_house", "Full House", _full_house),
    Category("small_straight", "Small Straight", _straight(4, 30)),
    Category("large_straight", "Large Straight", _straight(5, 40)),
    Category("yahtzee", "Yahtzee", _yahtzee),
    Category("chance", "Chance", sum),
)

CATEGORIES_BY_KEY: dict[str, Category] = {c.key: c for c in CATEGORIES}


@dataclass
class ScoreCard:
    """The thirteen categories for a single player, filled in one per turn."""

    scores: dict[str, int] = field(default_factory=dict)

    def is_open(self, key: str) -> bool:
        return key in CATEGORIES_BY_KEY and key not in self.scores

    def open_categories(self) -> list[Category]:
        return [c for c in CATEGORIES if self.is_open(c.key)]

    @property
    def is_complete(self) -> bool:
        return len(self.scores) == len(CATEGORIES)

    def record(self, key: str, dice: Sequence[int]) -> int:
        """Score `dice` in category `key` and return the points earned."""
        category = CATEGORIES_BY_KEY.get(key)
        if category is None:
            raise KeyError(f"Unknown category: {key}")
        if key in self.scores:
            raise ValueError(f"{category.label} is already filled in")

        points = category.score(dice)
        self.scores[key] = points
        return points

    @property
    def upper_subtotal(self) -> int:
        return sum(self.scores.get(c.key, 0) for c in CATEGORIES if c.upper)

    @property
    def upper_bonus(self) -> int:
        return UPPER_BONUS if self.upper_subtotal >= UPPER_BONUS_THRESHOLD else 0

    @property
    def lower_subtotal(self) -> int:
        return sum(self.scores.get(c.key, 0) for c in CATEGORIES if not c.upper)

    @property
    def total(self) -> int:
        return self.upper_subtotal + self.upper_bonus + self.lower_subtotal
