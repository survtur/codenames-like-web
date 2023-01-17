from pydantic import BaseModel


class Rules(BaseModel):
    cards_count: int
    cards_set: int
    team_cards_count: list[int]
    black_cards_count: int
    custom_cards: list[str] | None
