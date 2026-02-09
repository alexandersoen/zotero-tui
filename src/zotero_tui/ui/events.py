from textual.message import Message


class SearchChanged(Message):
  """Sent when the search query changes."""

  def __init__(self, query: str) -> None:
    self.query = query
    super().__init__()


class SearchClosed(Message):
  """Sent when the search bar is closed (Accepted or Cancelled)."""
