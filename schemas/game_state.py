from pydantic import BaseModel, Field


class Card(BaseModel):
    word: str  # word
    team: int  # team_id
    is_opened: int  # is_opened


class FullGameState(BaseModel):
    name: str  # name of a game
    cards: list[Card]  # cards in game


class RestrictesCard(BaseModel):
    word: str  # word
    team: int | None  # team_id


class RestrictedGameState(BaseModel):
    name: str  # name of a game
    cards: list[RestrictesCard]  # cards in game
    cards_left: list[int]
