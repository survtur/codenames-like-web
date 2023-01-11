import logging
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from conn_manager import ConnectionManager
from db.db import GamesDb
from game import full_state_to_restricted
from schemas.rules import Rules

app = FastAPI(docs_url=None, redoc_url=None)

with open(Path(__file__).parent.joinpath('index.html')) as f:
    page_html = f.read()

manager = ConnectionManager()
DB_PATH = Path("test.sqlite3")


@app.get("/")
async def root():
    return HTMLResponse(page_html)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """asdsad"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            await process_request(data, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)


async def init_game(rules: dict, websocket: WebSocket):
    rules = Rules.parse_obj(rules)
    d = GamesDb(DB_PATH)
    game_state = d.new_game(rules)
    name = game_state.name
    manager.set_game_name(websocket, name)
    state_dict = game_state.dict()
    data = {'success': True, 'state': state_dict, 'action': 'init', 'game': name, }
    await manager.send_to_game(data, name)


async def open_card(game: str, card_index: int):
    d = GamesDb(DB_PATH)
    game_state = d.get_game_state(game)

    card = game_state.cards[card_index]
    if not card.is_opened:
        card.is_opened = True
        d.update_game(game_state)

    await manager.send_to_game(
        {'success': True, 'card': card.dict(), 'card_id': card_index, 'action': 'open', 'game': game, },
        game_state.name)


async def get_state(websocket: WebSocket, game: str, restricted: bool):
    d = GamesDb(DB_PATH)
    game_state = d.get_game_state(game)
    if restricted:
        game_state = full_state_to_restricted(game_state)
    await websocket.send_json({'success': True, 'state': game_state.dict(), 'game': game,
                               'action': 'state' if restricted else 'full_state'})


async def process_request(data: dict, websocket: WebSocket):
    try:
        action: str = data['action']
        if action == "init":
            await init_game(data['rules'], websocket)
            return

        game: str = data['game']
        if action == "open":
            await open_card(game, data['card'])
        elif action == "state":
            await get_state(websocket, game, restricted=True)
        elif action == "full_state":
            await get_state(websocket, game, restricted=False)

    except (ValueError, RuntimeError, KeyError, TypeError) as e:
        logging.exception(e)
        await manager.send_json({"error": repr(e)}, manager._active_connections)
