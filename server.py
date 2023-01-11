from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from conn_manager import ConnectionManager
from db.db import GamesDb
from game import full_state_to_restricted
from schemas.rules import Rules

app = FastAPI(docs_url=None, redoc_url=None)

page_html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
            <input type="text" id="messageText" autocomplete="off"/>
            <button type="button" onclick="sendMessage()">Send</button>
            <button type="button" onclick="initGame()">Init</button>
            <button type="button" onclick="getState()">State</button>
            <button type="button" onclick="getReState()">ReState</button>
            <button type="button" onclick="openCard()">Open</button>
        <ul id='messages'>
        </ul>
        <script>
            let game = "";
            let ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = (event) => {
                const messages = document.getElementById('messages')
                const message = document.createElement('li')
                const content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
                let parsed = JSON.parse(event.data)
                console.log(parsed)
                
                if (parsed.action === "init") {
                    game = parsed.state.name
                }
            };
            function sendMessage(event) {
                let input = document.getElementById("messageText")
                ws.send(JSON.stringify(input.value))
                input.value = ''
                event.preventDefault()
            }
            function initGame(event) {
                const rules = {cards_count: 25, team_cards_count: [2,1], cards_set: 0, cards_for_first_team: 3};
                ws.send(JSON.stringify({action: 'init', rules: rules}))
            }
            function getState(event) {
                ws.send(JSON.stringify({action: 'full_state', 'game': game}))
            }
            function getReState(event) {
                ws.send(JSON.stringify({action: 'state', 'game': game}))
            }
            function openCard(event) {
                ws.send(JSON.stringify({action: 'open', 'card': 1, 'game': game}))
            }
        </script>
    </body>
</html>
"""

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
        await manager.send_json(f"Client left the chat", manager._active_connections)


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
        await manager.send_json({"error": repr(e)}, manager._active_connections)
