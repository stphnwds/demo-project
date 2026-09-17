"""Tests for the scoring rules, dice handling, and game flow."""

import random

import pytest

from src.yahtzee.cli import format_card, format_dice, parse_keep
from src.yahtzee.dice import MAX_ROLLS_PER_TURN, NUM_DICE, DiceCup
from src.yahtzee.game import Game
from src.yahtzee.scoring import CATEGORIES, UPPER_BONUS, CATEGORIES_BY_KEY, ScoreCard


def score(key, dice):
    return CATEGORIES_BY_KEY[key].score(dice)


@pytest.mark.parametrize(
    "key, dice, expected",
    [
        ("ones", [1, 1, 3, 4, 1], 3),
        ("ones", [2, 3, 4, 5, 6], 0),
        ("fours", [4, 4, 4, 2, 1], 12),
        ("sixes", [6, 6, 6, 6, 6], 30),
    ],
)
def test_upper_section_counts_only_matching_faces(key, dice, expected):
    assert score(key, dice) == expected


@pytest.mark.parametrize(
    "key, dice, expected",
    [
        ("three_of_a_kind", [3, 3, 3, 5, 2], 16),
        ("three_of_a_kind", [3, 3, 4, 5, 2], 0),
        ("four_of_a_kind", [2, 2, 2, 2, 6], 14),
        ("four_of_a_kind", [2, 2, 2, 5, 6], 0),
        ("four_of_a_kind", [5, 5, 5, 5, 5], 25),
    ],
)
def test_n_of_a_kind_totals_all_dice(key, dice, expected):
    assert score(key, dice) == expected


@pytest.mark.parametrize(
    "dice, expected",
    [
        ([3, 3, 2, 2, 2], 25),
        ([6, 6, 6, 1, 1], 25),
        ([4, 4, 4, 4, 4], 0),  # five of a kind is not a full house
        ([1, 1, 2, 2, 3], 0),
        ([5, 5, 5, 5, 2], 0),
    ],
)
def test_full_house(dice, expected):
    assert score("full_house", dice) == expected


@pytest.mark.parametrize(
    "dice, small, large",
    [
        ([1, 2, 3, 4, 6], 30, 0),
        ([2, 3, 4, 5, 5], 30, 0),
        ([1, 2, 3, 4, 5], 30, 40),
        ([2, 3, 4, 5, 6], 30, 40),
        ([1, 2, 2, 3, 6], 0, 0),
        ([1, 1, 1, 1, 1], 0, 0),
    ],
)
def test_straights(dice, small, large):
    assert score("small_straight", dice) == small
    assert score("large_straight", dice) == large


@pytest.mark.parametrize(
    "dice, expected", [([3, 3, 3, 3, 3], 50), ([3, 3, 3, 3, 2], 0)]
)
def test_yahtzee(dice, expected):
    assert score("yahtzee", dice) == expected


def test_chance_is_the_plain_total():
    assert score("chance", [1, 3, 3, 5, 6]) == 18


def test_upper_bonus_awarded_at_threshold():
    card = ScoreCard()
    for key, dice in [
        ("ones", [1, 1, 1, 2, 2]),        # 3
        ("twos", [2, 2, 2, 1, 1]),        # 6
        ("threes", [3, 3, 3, 1, 1]),      # 9
        ("fours", [4, 4, 4, 1, 1]),       # 12
        ("fives", [5, 5, 5, 1, 1]),       # 15
        ("sixes", [6, 6, 6, 1, 1]),       # 18
    ]:
        card.record(key, dice)

    assert card.upper_subtotal == 63
    assert card.upper_bonus == UPPER_BONUS
    assert card.total == 63 + UPPER_BONUS


def test_no_upper_bonus_below_threshold():
    card = ScoreCard()
    card.record("sixes", [6, 6, 6, 1, 1])
    assert card.upper_subtotal == 18
    assert card.upper_bonus == 0
    assert card.total == 18


def test_total_combines_both_sections():
    card = ScoreCard()
    card.record("fives", [5, 5, 5, 1, 1])   # 15
    card.record("yahtzee", [4, 4, 4, 4, 4])  # 50
    assert card.total == 65


def test_category_cannot_be_used_twice():
    card = ScoreCard()
    card.record("chance", [1, 2, 3, 4, 5])
    with pytest.raises(ValueError):
        card.record("chance", [6, 6, 6, 6, 6])


def test_unknown_category_rejected():
    with pytest.raises(KeyError):
        ScoreCard().record("nope", [1, 2, 3, 4, 5])


def test_open_categories_shrink_as_they_are_filled():
    card = ScoreCard()
    assert len(card.open_categories()) == len(CATEGORIES)
    card.record("ones", [1, 1, 1, 1, 1])
    assert not card.is_open("ones")
    assert len(card.open_categories()) == len(CATEGORIES) - 1
    assert not card.is_complete


def test_card_is_complete_once_every_category_is_used():
    card = ScoreCard()
    for category in CATEGORIES:
        card.record(category.key, [1, 2, 3, 4, 5])
    assert card.is_complete
    assert card.open_categories() == []


def test_roll_produces_five_dice_in_range():
    cup = DiceCup(random.Random(7))
    dice = cup.roll()
    assert len(dice) == NUM_DICE
    assert all(1 <= d <= 6 for d in dice)


def test_held_dice_survive_a_reroll():
    cup = DiceCup(random.Random(7))
    cup.roll()
    kept = cup.dice[0], cup.dice[2]
    cup.roll(keep={1, 3})
    assert (cup.dice[0], cup.dice[2]) == kept


def test_turn_is_limited_to_three_rolls():
    cup = DiceCup(random.Random(7))
    for _ in range(MAX_ROLLS_PER_TURN):
        cup.roll()
    assert cup.rolls_left == 0
    with pytest.raises(ValueError):
        cup.roll()

    cup.reset()
    assert cup.rolls_left == MAX_ROLLS_PER_TURN


def test_reroll_rejects_out_of_range_positions():
    cup = DiceCup(random.Random(7))
    with pytest.raises(ValueError):
        cup.roll(keep={0, 9})


def test_same_seed_gives_the_same_dice():
    a = DiceCup(random.Random(99)).roll()
    b = DiceCup(random.Random(99)).roll()
    assert a == b


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("1 3 5", {1, 3, 5}),
        ("1,3,5", {1, 3, 5}),
        ("  2 ", {2}),
        ("", set()),
        ("none", set()),
        ("all", {1, 2, 3, 4, 5}),
        ("ALL", {1, 2, 3, 4, 5}),
    ],
)
def test_parse_keep(raw, expected):
    assert parse_keep(raw) == expected


@pytest.mark.parametrize("raw", ["x", "0", "6", "1 9"])
def test_parse_keep_rejects_bad_input(raw):
    with pytest.raises(ValueError):
        parse_keep(raw)


def test_game_requires_a_player():
    with pytest.raises(ValueError):
        Game([])


def test_game_turn_and_completion():
    game = Game(["A", "B"], random.Random(1))
    player = game.players[0]

    game.start_turn()
    assert game.cup.rolls_left == MAX_ROLLS_PER_TURN - 1
    game.reroll(keep={1, 2})
    points = game.take_category(player, "chance")

    assert points == sum(game.cup.dice)
    assert player.total == points
    assert not game.is_over


def test_full_match_fills_every_card():
    game = Game(["A", "B"], random.Random(3))
    for _ in range(game.rounds):
        for player in game.players:
            game.start_turn()
            key = player.card.open_categories()[0].key
            game.take_category(player, key)

    assert game.is_over
    assert all(p.card.is_complete for p in game.players)
    assert game.standings()[0].total >= game.standings()[-1].total


def test_winners_include_every_tied_player():
    game = Game(["A", "B"], random.Random(5))
    for player in game.players:
        player.card.record("chance", [1, 1, 1, 1, 1])

    winners = game.winners()
    assert {w.name for w in winners} == {"A", "B"}


def test_rendering_helpers_run():
    dice = [1, 2, 3, 4, 5]
    assert "positions" in format_dice(dice)

    card = ScoreCard()
    card.record("ones", [1, 1, 1, 2, 3])
    rendered = format_card(card, dice)
    assert "Large Straight" in rendered
    assert "TOTAL" in rendered
