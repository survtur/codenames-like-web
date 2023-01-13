import json
import os
import sqlite3
import time
from pathlib import Path

from game import create_game_set
from name_generator import create_fake_word_len
from schemas.game_state import FullGameState
from schemas.rules import Rules


class GamesDb:

    def __init__(self, file: Path | str):
        self.__connection: sqlite3.Connection | None = None
        self._file: Path | str = file

    @property
    def _conn(self) -> sqlite3.Connection:
        if self.__connection is None:
            exist = os.path.exists(self._file)
            self.__connection = sqlite3.connect(self._file)
            if not exist:
                self._initialise_db()
        return self.__connection

    def _initialise_db(self):
        script_file = os.path.join(os.path.dirname(__file__), 'init_script.sqllite3')
        with open(script_file) as f:
            script = f.read()
        self.__connection.executescript(script)

    def new_game(self, r: Rules) -> FullGameState:
        game_state = create_game_set(r)

        max_retries = 50
        retries = 0
        while True:
            try:
                game_state.name = create_fake_word_len(2, 3, min_len=5).upper()
                self._conn.execute('INSERT INTO Games (name, modified, data) VALUES (:n, :m, :d)',
                                   {'n': game_state.name, 'm': int(time.time()), 'd': game_state.json()})
                self._conn.commit()
                return game_state
            except sqlite3.IntegrityError as e:
                retries += 1
                if "Games.n" in str(e) and retries != max_retries:
                    continue
                raise e

    def update_game(self, s: FullGameState):
        self._conn.execute('UPDATE Games SET modified=:m, data=:d WHERE name=:n',
                           {'n': s.name, 'm': int(time.time()), 'd': s.json()})
        self._conn.commit()

    def get_game_state(self, game_name: str) -> FullGameState:
        cur = self._conn.execute('SELECT data FROM Games WHERE name=?', (game_name,))
        data = json.loads(cur.fetchone()[0])
        return FullGameState.parse_obj(data)

    def _remove_old(self):
        raise NotImplemented
