"""Text interface for playing a game at the terminal."""

import argparse
import random
from typing import Sequence

from src.yahtzee.dice import NUM_DICE
from src.yahtzee.game import Game, Player
from src.yahtzee.scoring import CATEGORIES, UPPER_BONUS_THRESHOLD, ScoreCard

DIE_FACES = {1: "⚀", 2: "⚁", 3: "⚂", 4: "⚃", 5: "⚄", 6: "⚅"}


def format_dice(dice: Sequence[int]) -> str:
    positions = "   ".join(f"{i}" for i in range(1, len(dice) + 1))
    faces = "   ".join(f"{DIE_FACES[d]}" for d in dice)
    values = "   ".join(str(d) for d in dice)
    return f"  {faces}\n  {values}\n  {positions}  <- positions"


def format_card(card: ScoreCard, dice: Sequence[int] | None = None) -> str:
    """Render a score card; with `dice`, open lines show what they would score."""
    lines = ["  #   Category           Score", "  " + "-" * 34]
    for i, category in enumerate(CATEGORIES, start=1):
        if i == 7:
            lines.append(f"      {'Upper subtotal':<18} {card.upper_subtotal:>5}"
                         f"   (bonus at {UPPER_BONUS_THRESHOLD}: +{card.upper_bonus})")
            lines.append("  " + "-" * 34)
        if category.key in card.scores:
            value = f"{card.scores[category.key]:>5}"
            marker = " "
        elif dice:
            value = f"{category.score(dice):>5}"
            marker = "*"
        else:
            value = "    -"
            marker = " "
        lines.append(f" {marker}{i:>2}   {category.label:<18} {value}")
    lines.append("  " + "-" * 34)
    lines.append(f"      {'TOTAL':<18} {card.total:>5}")
    if dice:
        lines.append("  * = what this roll would score")
    return "\n".join(lines)


def parse_keep(raw: str) -> set[int]:
    """Turn user input such as '1 3 5', 'all' or '' into a set of positions."""
    text = raw.strip().lower()
    if text in {"all", "a", "keep"}:
        return set(range(1, NUM_DICE + 1))
    if text in {"", "none", "n"}:
        return set()

    keep = set()
    for token in text.replace(",", " ").split():
        if not token.isdigit():
            raise ValueError(f"'{token}' is not a die position")
        position = int(token)
        if not 1 <= position <= NUM_DICE:
            raise ValueError(f"Die positions run 1-{NUM_DICE}, got {position}")
        keep.add(position)
    return keep


def prompt_keep(dice: Sequence[int], rolls_left: int) -> set[int]:
    while True:
        raw = input(
            f"  Keep which dice? (positions, 'all', or Enter to reroll all) "
            f"[{rolls_left} roll(s) left]: "
        )
        try:
            return parse_keep(raw)
        except ValueError as exc:
            print(f"  {exc}")


def prompt_category(card: ScoreCard, dice: Sequence[int]) -> str:
    """Ask for a category by number or name, accepting only open ones."""
    open_keys = {c.key for c in card.open_categories()}
    numbered = {str(i): c for i, c in enumerate(CATEGORIES, start=1)}

    while True:
        raw = input("  Score this roll as (number or name): ").strip().lower()
        category = numbered.get(raw)
        if category is None:
            matches = [
                c for c in CATEGORIES
                if c.key == raw.replace(" ", "_") or c.label.lower() == raw
            ]
            category = matches[0] if matches else None

        if category is None:
            print("  No such category. Use the numbers shown on the card.")
        elif category.key not in open_keys:
            print(f"  {category.label} is already filled in. Pick another.")
        else:
            return category.key


def play_turn(game: Game, player: Player, round_number: int) -> None:
    print(f"\n{'=' * 40}\nRound {round_number}/{game.rounds} - {player.name}\n{'=' * 40}")
    dice = game.start_turn()
    print(format_dice(dice))

    while game.cup.rolls_left > 0:
        keep = prompt_keep(dice, game.cup.rolls_left)
        if len(keep) == NUM_DICE:
            print("  Keeping all five.")
            break
        dice = game.reroll(keep)
        print(format_dice(dice))

    print(f"\nFinal roll: {' '.join(str(d) for d in dice)}\n")
    print(format_card(player.card, dice))
    key = prompt_category(player.card, dice)
    points = game.take_category(player, key)
    print(f"  Scored {points} point(s). {player.name} now has {player.total}.")


def announce_results(game: Game) -> None:
    print(f"\n{'=' * 40}\nFinal scores\n{'=' * 40}")
    for player in game.standings():
        print(f"\n{player.name}: {player.total}")
        print(format_card(player.card))

    winners = game.winners()
    if len(winners) == 1:
        print(f"\n{winners[0].name} wins with {winners[0].total} points!")
    else:
        names = ", ".join(w.name for w in winners)
        print(f"\nIt's a tie between {names} at {winners[0].total} points!")


def prompt_players() -> list[str]:
    raw = input("Player names (comma separated, Enter for a solo game): ").strip()
    names = [n.strip() for n in raw.split(",") if n.strip()]
    return names or ["Player 1"]


def play(names: Sequence[str] | None = None, seed: int | None = None) -> Game:
    print("\nYahtzee - five dice, three rolls a turn, thirteen rounds.\n")
    names = list(names) if names else prompt_players()
    game = Game(names, random.Random(seed))

    for round_number in range(1, game.rounds + 1):
        for player in game.players:
            play_turn(game, player, round_number)

    announce_results(game)
    return game


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Play a simple game of Yahtzee.")
    parser.add_argument("names", nargs="*", help="player names (prompted for if omitted)")
    parser.add_argument("--seed", type=int, help="seed the dice for a repeatable game")
    args = parser.parse_args(argv)

    try:
        play(args.names, args.seed)
    except (EOFError, KeyboardInterrupt):
        print("\nGame abandoned.")
        return 1
    return 0
