import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator


class ZoteroDB:
  def __init__(self, db_path: Path) -> None:
    self.db_path = db_path.expanduser()
    self._watcher_conn: sqlite3.Connection | None = None
    self._last_version: int | None = None

  @contextmanager
  def connect(self) -> Generator[sqlite3.Connection, None, None]:
    conn = sqlite3.connect(f"file:{self.db_path}?mode=ro&nolock=1", uri=True)
    conn.row_factory = sqlite3.Row

    try:
      conn.execute("PRAGMA busy_timeout=5000;")
      yield conn
    finally:
      conn.close()

  @property
  def watcher_conn(self) -> sqlite3.Connection:
    if self._watcher_conn is None:
      self._watcher_conn = sqlite3.connect(
        f"file:{self.db_path}?mode=ro&nolock=1", uri=True
      )

    return self._watcher_conn

  def get_data_version(self) -> int:
    cur = self.watcher_conn.execute("PRAGMA data_version;")
    return cur.fetchone()[0]

  def has_update(self) -> bool:
    cur_version = self.get_data_version()
    if self._last_version is None:
      self._last_version = cur_version
      return False

    if self._last_version != cur_version:
      self._last_version = cur_version
      return True

    return False


if __name__ == "__main__":
  zotero_db_path = Path("/Users/alexander.soen/Zotero/zotero.sqlite")
  db = ZoteroDB(zotero_db_path)

  with db.connect() as conn:
    count = conn.execute("SELECT COUNT(*) FROM items").fetchone()[0]
    print(f"📚 Your library has {count} items.")
