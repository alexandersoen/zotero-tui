import sqlite3

from contextlib import contextmanager
from pathlib import Path
from typing import Generator


class ZoteroDB:
  def __init__(self, db_path: Path) -> None:
    self.db_path = db_path.expanduser()

  @contextmanager
  def connect(self) -> Generator[sqlite3.Connection, None, None]:
    conn = sqlite3.connect(f"file:{self.db_path}?mode=ro&nolock=1", uri=True)
    conn.row_factory = sqlite3.Row

    try:
      conn.execute("PRAGMA busy_timeout=5000;")
      yield conn
    finally:
      conn.close()


if __name__ == "__main__":
  zotero_db_path = Path("/Users/alexander.soen/Zotero/zotero.sqlite")
  db = ZoteroDB(zotero_db_path)

  with db.connect() as conn:
    count = conn.execute("SELECT COUNT(*) FROM items").fetchone()[0]
    print(f"📚 Your library has {count} items.")
