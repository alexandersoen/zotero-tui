from textual.widgets import Static


class StatusBar(Static):
  """Displays item counts and application state."""

  def update_all(self, sort_desc: str, found: int, total: int) -> None:
    self.update(f"Sort: {sort_desc}  |  [b]{found}[/b] / {total} items")
