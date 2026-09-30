import sqlite3
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from . import config

TZ = ZoneInfo("Asia/Taipei")
def now():
    return datetime.now(TZ)

def _conn():
    config.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(config.DB_PATH)
    c.row_factory = sqlite3.Row
    c.execute("""CREATE TABLE IF NOT EXISTS forecast(
        location TEXT, start_time TEXT, end_time TEXT, wx TEXT, pop INT,
        min_t INT, max_t INT, ci TEXT, fetched_at TEXT,
        PRIMARY KEY(location, start_time))""")
    return c

def save(rows):
    ts = now().isoformat(timespec="seconds")
    cutoff = (now() - timedelta(days=config.RETENTION_DAYS)).strftime("%Y-%m-%d %H:%M:%S")
    with _conn() as c:
        c.executemany("""INSERT OR REPLACE INTO forecast VALUES
            (:location,:start,:end,:wx,:pop,:min_t,:max_t,:ci,:ts)""",
            [{**r, "ts": ts} for r in rows])
        c.execute("DELETE FROM forecast WHERE end_time < ?", (cutoff,))
    return ts

def last_fetch():
    with _conn() as c:
        v = c.execute("SELECT MAX(fetched_at) m FROM forecast").fetchone()["m"]
    return datetime.fromisoformat(v) if v else None

def load(location):
    n = now().strftime("%Y-%m-%d %H:%M:%S")
    with _conn() as c:
        cur = c.execute("""SELECT * FROM forecast WHERE location=? AND end_time>=?
                           ORDER BY start_time""", (location, n))
        return [dict(r) for r in cur]
