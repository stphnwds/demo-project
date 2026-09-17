"""Rolling and holding the five dice."""

import random

NUM_DICE = 5
NUM_SIDES = 6
MAX_ROLLS_PER_TURN = 3


class DiceCup:
    """Five dice that can be rolled, partially held, and rolled again."""

    def __init__(self, rng: random.Random | None = None) -> None:
        self.rng = rng or random.Random()
        self.dice: list[int] = [0] * NUM_DICE
        self.rolls_used = 0

    @property
    def rolls_left(self) -> int:
        return MAX_ROLLS_PER_TURN - self.rolls_used

    def reset(self) -> None:
        """Start a fresh turn."""
        self.dice = [0] * NUM_DICE
        self.rolls_used = 0

    def roll(self, keep: set[int] | None = None) -> list[int]:
        """Roll every die whose 1-based position is not in `keep`.

        Raises ValueError when no rolls are left in the turn.
        """
        if self.rolls_left <= 0:
            raise ValueError("No rolls left this turn")

        keep = keep or set()
        invalid = {i for i in keep if not 1 <= i <= NUM_DICE}
        if invalid:
            raise ValueError(f"Dice positions must be 1-{NUM_DICE}, got {sorted(invalid)}")

        for i in range(NUM_DICE):
            if (i + 1) not in keep:
                self.dice[i] = self.rng.randint(1, NUM_SIDES)

        self.rolls_used += 1
        return list(self.dice)
