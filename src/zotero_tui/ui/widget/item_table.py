from typing import Any
from textual.widgets import DataTable
from zotero_tui.database.models import ZoteroItem


class ZoteroTable(DataTable):
  """A DataTable that handles its own filtering logic."""

  def __init__(self, **kwargs: Any):
    super().__init__(**kwargs)
    self.master_items: list[ZoteroItem] = []

  def on_mount(self) -> None:
    self.cursor_type = "row"
    self.add_columns("Year", "Author", "Title")

  def load_data(self, items: list[ZoteroItem]) -> None:
    """Initial data load."""
    self.master_items = items
    self.apply_filter("")

  def apply_filter(self, query: str) -> int:
    """Clears the table and re-adds rows based on query."""
    self.clear()
    filtered = [item for item in self.master_items if item.is_query_match(query)]

    for item in filtered:
      self.add_row(
        str(item.year) if item.year > 0 else "----",
        item.author_summary,
        item.title,
        key=str(item.item_id),
      )

    return len(filtered)
