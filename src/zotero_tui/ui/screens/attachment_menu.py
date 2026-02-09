from textual import events
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import OptionList, Label
from textual.containers import Vertical
from zotero_tui.database.models import Attachment


class AttachmentMenu(ModalScreen[Attachment]):
  """A modal dialog to select from multiple attachments."""

  def __init__(self, attachments: list[Attachment]):
    super().__init__()
    self.attachments = attachments

  def compose(self) -> ComposeResult:
    with Vertical(id="dialog"):
      yield Label("Select Attachment:", id="dialog-title")
      # List all attachments by their filename
      yield OptionList(
        *[att.path.name for att in self.attachments], id="attachment-list"
      )
      yield Label("j/k: Navigate | Enter: Select | Esc: Cancel", id="dialog-footer")

  def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
    # Return the actual attachment object back to the app
    self.dismiss(self.attachments[event.option_index])

  def on_key(self, event: events.Key) -> None:
    """Handle Vim navigation and Escape key."""
    option_list = self.query_one(OptionList)

    if event.key == "j":
      option_list.action_cursor_down()
    elif event.key == "k":
      option_list.action_cursor_up()
    elif event.key == "escape":
      self.dismiss(None)
