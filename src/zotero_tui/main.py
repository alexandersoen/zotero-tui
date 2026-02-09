from pathlib import Path
from zotero_tui.database.connection import ZoteroDB
from zotero_tui.database.queries import fetch_all_items
from zotero_tui.ui.app import ZoteroApp


def run_app():
  # 1. Setup DB
  p = Path("~/Zotero/zotero.sqlite")
  db = ZoteroDB(p)

  # 2. Get Data (Functional approach)
  with db.connect() as conn:
    items = list(fetch_all_items(conn))

  # 3. Pass items to Textual App
  app = ZoteroApp(items=items)
  app.run()


if __name__ == "__main__":
  run_app()
