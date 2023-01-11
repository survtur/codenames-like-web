BEGIN;
CREATE TABLE Games (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            modified INTEGER NOT NULL,
            data TEXT NOT NULL
        );
COMMIT;