from pathlib import Path
from zotero_tui.database.connection import ZoteroDB
from zotero_tui.ui.app import ZoteroApp


def run_app():
  p = Path("~/Zotero/zotero.sqlite")
  db = ZoteroDB(p)

  app = ZoteroApp(db=db)
  app.run()


if __name__ == "__main__":
  run_app()
