from pydantic import BaseModel


class Card(BaseModel):
    word: str  # word
    team: int  # team_id
    is_opened: bool  # is_opened


class FullGameState(BaseModel):
    name: str  # name of a game
    cards: list[Card]  # cards in game
    winner: int | None
    score: list[int]
