from collections.abc import Iterable
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self._active_connections: set[WebSocket] = set()
        self._ws_to_game: dict[WebSocket, str] = dict()
        self._game_to_ws: dict[str, list[WebSocket]] = dict()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        print(f'Connected {websocket.client}. Active connections count: {len(self._active_connections)}.')
        self._active_connections.add(websocket)

    def _remove_ws_from_game(self, websocket: WebSocket):
        game = self._ws_to_game.get(websocket)
        if game:
            self._game_to_ws[game].remove(websocket)
            self._ws_to_game.pop(websocket)

    def set_game_name(self, websocket: WebSocket, game_name: str):
        self._ws_to_game[websocket] = game_name
        if game_name not in self._game_to_ws:
            self._game_to_ws[game_name] = []
        self._game_to_ws[game_name].append(websocket)

    def disconnect(self, websocket: WebSocket):
        self._active_connections.remove(websocket)
        print(f'Disconnected {websocket.client}. Active connections count: {len(self._active_connections)}.')

    async def send_to_game(self, data: any, game_name: str):
        await self.send_json(data, self._game_to_ws[game_name])

    @staticmethod
    async def send_json(data: any, ws: Iterable[WebSocket]):
        for s in ws:
            await s.send_json(data)
