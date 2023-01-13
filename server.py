import logging
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from conn_manager import ConnectionManager
from db.db import GamesDb
from game import update_game_stats
from schemas.game_state import FullGameState
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
    data = {'success': True, 'action': 'init', 'game': game_state.name}
    manager.set_game_name(websocket, game_state.name)
    await manager.send_to_game(data, game_state.name)


def open_card(game: str, card_index: int) -> FullGameState:
    d = GamesDb(DB_PATH)
    game_state = d.get_game_state(game)

    card = game_state.cards[card_index]
    if not card.is_opened:
        card.is_opened = True
        update_game_stats(game_state)
        d.update_game(game_state)

    return game_state


def get_state(game: str) -> FullGameState:
    d = GamesDb(DB_PATH)
    return d.get_game_state(game)


async def process_request(data: dict, websocket: WebSocket):
    try:
        action: str = data['action']
        if action == "init":
            await init_game(data['rules'], websocket)
            return

        game: str = data['game']
        manager.set_game_name(websocket, game)
        if action == "open":
            state = open_card(game, data['card'])
            await _send_game_state(state)
        elif action == "join":
            state = get_state(game)
            await _send_game_state(state, websocket)

    except (ValueError, RuntimeError, KeyError, TypeError) as e:
        logging.exception(e)
        await manager.send_json({"error": repr(e)}, [websocket])


async def _send_game_state(s: FullGameState, ws_to_use: WebSocket | None = None):
    data = {'success': True, 'action': 'state', 'state': s.dict(), 'game': s.name}
    if not ws_to_use:
        await manager.send_to_game(data, s.name)
    else:
        await manager.send_json(data, [ws_to_use])
