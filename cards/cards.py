from pathlib import Path


def get_cards(collection_id: int) -> list[str]:
    this_dir = Path(__file__).parent
    cards_list = this_dir.joinpath(str(collection_id)).joinpath('list.txt')
    with open(cards_list) as f:
        lines = f.readlines()
        lines = [x.strip() for x in lines]
        lines = [x for x in lines if x]
        return lines
