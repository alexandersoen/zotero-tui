from textual.widgets import Static


class StatusBar(Static):
  """Displays item counts and application state."""

  def update_counts(self, found: int, total: int) -> None:
    self.update(f" [b]{found}[/b] / {total} items found ")
