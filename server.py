from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from conn_manager import ConnectionManager
from db.db import GamesDb
from schemas.rules import Rules

app = FastAPI()


def a():
    return 33


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
            <button type="button">Open</button>
        <ul id='messages'>
        </ul>
        <script>
            let ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = (event) => {
                const messages = document.getElementById('messages')
                const message = document.createElement('li')
                const content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
                console.log(JSON.parse(event.data))
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
    manager.set_game_name(websocket, game_state.name)
    await manager.send_to_game(game_state.dict(), game_state.name)


def open_card(game: str, data):
    d = GamesDb(DB_PATH)
    raise NotImplementedError


async def process_request(data: dict, websocket: WebSocket):
    try:
        action: str = data['action']
        if action == "init":
            await init_game(data['rules'], websocket)
        elif action == "open":
            game: str = data['game']
            open_card(game, data['open'])
    except (ValueError, RuntimeError, KeyError) as e:
        await manager.send_json({"error": repr(e)}, manager._active_connections)
