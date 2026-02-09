from textual.containers import Horizontal
from textual.widgets import Input, Static

from zotero_tui.ui.events import SearchChanged, SearchClosed


class SearchBar(Horizontal):
  """Vim-style search bar that posts SearchChanged messages."""

  def compose(self):
    yield Static("/", id="prompt")
    yield Input(placeholder="search...", id="search-input")

  def on_mount(self) -> None:
    # Ensure the input doesn't have any hidden constraints
    self.query_one(Input).styles.width = "100%"

  def on_input_changed(self, event: Input.Changed) -> None:
    # We don't filter here; we just notify the parent
    self.post_message(SearchChanged(event.value))

  def on_input_submitted(self, _: Input.Submitted) -> None:
    """Triggered on Enter."""
    self.close_search()

  def close_search(self) -> None:
    """Centralized closing logic."""
    self.display = False
    self.post_message(SearchClosed())  # Tell the App to clean up
    self.app.query_one("ZoteroTable").focus()
