from itertools import cycle
from typing import Any, Callable, NamedTuple

from textual.widgets import DataTable

from zotero_tui.database.models import ZoteroItem


class SortOrder(NamedTuple):
  display_str: str
  key_func: Callable[[ZoteroItem], Any]
  reverse: bool


SORT_ORDERING = cycle(
  [
    SortOrder("ID (↓)", lambda x: x.item_id, True),
    SortOrder("ID (↑)", lambda x: x.item_id, False),
    SortOrder("Year (↓)", lambda x: x.year, True),
    SortOrder("Year (↑)", lambda x: x.year, False),
    SortOrder("Title (↓)", lambda x: x.title, True),
    SortOrder("Title (↑)", lambda x: x.title, False),
  ]
)


class ZoteroTable(DataTable):
  """A DataTable that handles its own filtering logic."""

  def __init__(self, **kwargs: Any):
    super().__init__(**kwargs)
    self.master_items: list[ZoteroItem] = []

  def on_mount(self) -> None:
    self.cursor_type = "row"
    self.add_columns("Year", "Author", "Title")

  def load_data(
    self, items: list[ZoteroItem], sort_order: SortOrder | None = None
  ) -> None:
    """Initial data load."""
    self.master_items = items
    self.apply_filter("", sort_order)

  def apply_filter(self, query: str, sort_order: SortOrder | None = None) -> int:
    """Clears the table and re-adds rows based on query."""
    self.clear()
    filtered = [item for item in self.master_items if item.is_query_match(query)]
    if sort_order:
      filtered = sorted(filtered, key=sort_order.key_func, reverse=sort_order.reverse)

    for item in filtered:
      self.add_row(
        str(item.year) if item.year > 0 else "----",
        item.author_summary,
        item.title,
        key=str(item.item_id),
      )

    return len(filtered)
