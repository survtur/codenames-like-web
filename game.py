import enum
import random

from cards.cards import get_cards
from schemas.game_state import Card, FullGameState
from schemas.rules import Rules


class SpecialTeam(enum.IntEnum):
    BLACK = -2
    NEUTRAL = -1


def update_game_stats(s: FullGameState):
    counters = [0] * len(s.score)
    for c in s.cards:
        if not c.is_opened:
            if c.team >= 0:
                counters[c.team] += 1

    s.score = counters

    _update_winner(s)


def _update_winner(s: FullGameState):
    """
    Set winner if there was no winner.
    Black team wins if black cards exist and all of them was opened.
    Other team can win if its score is 0.
    """
    if s.winner is None:
        black_is_opened = [c.is_opened for c in s.cards if c.team == SpecialTeam.BLACK]
        if black_is_opened and all(black_is_opened):
            s.winner = SpecialTeam.BLACK
            return

        if 0 in s.score:
            s.winner = s.score.index(0)


def create_game_set(r: Rules) -> FullGameState:
    assert sum(r.team_cards_count) + r.black_cards_count < r.cards_count, 'Not enoungh cards to get enougn team cards'
    assert min(r.team_cards_count) > 0, 'Team cards should be greater than 0'
    all_cards = r.custom_cards or get_cards(r.cards_set)
    assert r.cards_count <= len(all_cards), 'Not enoungh card in deck'
    random.shuffle(all_cards)

    cards = [Card(word=c, team=SpecialTeam.NEUTRAL, is_opened=False) for c in all_cards[:r.cards_count]]

    # Assign BLACK CARDS
    for i in range(r.black_cards_count):
        cards[i].team = SpecialTeam.BLACK

    # Assign other teams
    index = r.black_cards_count  # Start with index 1, because index 0 is BLACK
    for team_id, card_count in enumerate(r.team_cards_count):
        for n in range(card_count):
            cards[index].team = team_id
            index += 1

    random.shuffle(cards)
    return FullGameState(name="", cards=cards, winner=None, score=r.team_cards_count)

