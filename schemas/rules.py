from pydantic import BaseModel


class Rules(BaseModel):
    cards_count: int
    cards_set: int
    team_cards_count: list[int]
    custom_cards: list[str] | None
