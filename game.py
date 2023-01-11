import enum
import random

from cards.cards import get_cards
from schemas.game_state import Card, FullGameState


class SpecialTeam(enum.IntEnum):
    BLACK = -2
    NEUTRAL = -1


def create_game_set(rules) -> FullGameState:
    assert sum(rules.team_cards_count) < rules.cards_count, 'Not enoungh c to get enougn team c'
    all_cards = rules.custom_cards or get_cards(rules.cards_set)
    assert rules.cards_count <= len(all_cards), 'Not enoungh card in deck'
    random.shuffle(all_cards)

    cards = [Card(word=c, team=SpecialTeam.NEUTRAL, is_opened=False) for c in all_cards[:rules.cards_count]]

    # Assign BLACK CARD
    cards[0].team = SpecialTeam.BLACK

    # Assign other teams
    index = 1  # Start with index 1, because index 0 is BLACK
    for team_id, card_count in enumerate(rules.team_cards_count):
        for n in range(card_count):
            cards[index].team = team_id
            index += 1

    random.shuffle(cards)
    return FullGameState(name="", cards=cards)
