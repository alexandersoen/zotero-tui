from textual.reactive import reactive
from textual.widgets import Static


class StatusBar(Static):
  """Displays item counts and application state."""

  sort_description: reactive[str] = reactive("ID (↓)")
  found: reactive[int] = reactive(0)
  total: reactive[int] = reactive(0)

  def watch_sort_description(self, _: str) -> None:
    self._update_display()

  def watch_found(self, _: int) -> None:
    self._update_display()

  def watch_total(self, _: int) -> None:
    self._update_display()

  def _update_display(self) -> None:
    self.update(
      f"Sort: {self.sort_description}  |  [b]{self.found}[/b] / {self.total} items"
    )

  def update_all(self, sort_desc: str, found: int, total: int) -> None:
    self.sort_description = sort_desc
    self.found = found
    self.total = total
