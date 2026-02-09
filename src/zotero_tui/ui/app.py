from pathlib import Path
from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import DataTable, Input, Static, Footer, Header
from textual.binding import Binding

from zotero_tui.database.models import Attachment, ZoteroItem
from zotero_tui.ui.events import SearchChanged, SearchClosed
from zotero_tui.ui.screens.attachment_menu import AttachmentMenu
from zotero_tui.ui.widget.item_table import ZoteroTable
from zotero_tui.ui.widget.search_bar import SearchBar
# from zotero_tui.ui.widget.status_bar import StatusBar
from zotero_tui.utils.system import open_file


class ZoteroApp(App):
  CSS_PATH = "styles.tcss"

  # VIM BINDINGS
  BINDINGS = [
    Binding("q", "quit", "Quit", show=True),
    Binding("j", "cursor_down", "Down", show=False),
    Binding("k", "cursor_up", "Up", show=False),
    Binding("ctrl+d", "page_down", "Page Down", show=False),
    Binding("ctrl+u", "page_up", "Page Up", show=False),
    Binding("gg", "scroll_home", "Top", show=False),
    Binding("G", "scroll_end", "Bottom", show=False),
    Binding("/", "focus_search", "Search", show=True),
    Binding("V", "view_pdf", "View PDF", show=True),
    Binding("escape", "cancel_search", "Normal Mode", show=False),
  ]

  def __init__(self, items: list[ZoteroItem]) -> None:
    super().__init__()
    self.items_data = {item.item_id: item for item in items}

  # --- Setup ---
  def compose(self) -> ComposeResult:
    yield Header()
    with Horizontal(id="container"):
      yield ZoteroTable(id="main-table")
      yield Static(id="detail-panel")

    yield SearchBar(id="search-bar")
    yield Footer()

  def on_mount(self) -> None:
    items = list(self.items_data.values())

    # self.query_one(StatusBar).update_counts(len(items), len(items))

    table = self.query_one(ZoteroTable)
    table.load_data(items)
    table.focus()

  # --- Event Handlers ---
  def on_search_changed(self, message: SearchChanged) -> None:
    table = self.query_one(ZoteroTable)
    table.apply_filter(message.query)
    # count =
    # total = len(table.master_items)

    # self.query_one(StatusBar).update_counts(count, total)

  def on_search_closed(self, _: SearchClosed) -> None:
    """Cleanup when search finishes."""
    self.remove_class("searching")

  def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
    """Update the abstract panel when moving with j/k."""
    if event.row_key is None or event.row_key.value is None:
      return

    item_id = int(event.row_key.value)
    item = self.items_data[item_id]

    detail_panel = self.query_one("#detail-panel", Static)
    content = f"[b]{item.title}[/b] ({item.item_id})\n\n[i]{item.author_summary}[/i]"  # \n\n{item.abstract}"
    detail_panel.update(content)

  # --- Actions ---
  def action_cursor_down(self) -> None:
    self.query_one(ZoteroTable).action_cursor_down()

  def action_cursor_up(self) -> None:
    self.query_one(ZoteroTable).action_cursor_up()

  def action_page_down(self) -> None:
    """Scroll half a page down (Vim ctrl+d)."""
    self.query_one(ZoteroTable).action_page_down()

  def action_page_up(self) -> None:
    """Scroll half a page up (Vim ctrl+u)."""
    self.query_one(ZoteroTable).action_page_up()

  def action_focus_search(self) -> None:
    self.add_class("searching")

    bar = self.query_one(SearchBar)
    bar.display = True
    bar.query_one(Input).focus()

  def action_cancel_search(self) -> None:
    """Handle ESC key at the App level."""
    bar = self.query_one(SearchBar)
    if bar.display:
      bar.close_search()  # This triggers the cleanup via message

  def action_view_pdf(self) -> None:
    """Placeholder for opening external PDF viewer."""
    table = self.query_one(ZoteroTable)
    cell_key = table.coordinate_to_cell_key(table.cursor_coordinate)
    if cell_key.row_key is None or cell_key.row_key.value is None:
      return

    item_id = int(cell_key.row_key.value)
    item = self.items_data[item_id]
    self._handle_pdf_launch(item)

  # --- Helpers ---
  def _handle_pdf_launch(self, item: ZoteroItem) -> None:
    if not item.attachments:
      self.notify("No PDF attached", severity="error")

    if len(item.attachments) == 1:
      # Single attachment? Open immediately
      self._open_attachment(item.attachments[0])
    else:
      # Multiple? Ask the user
      def handle_selection(attachment: Attachment | None):
        if attachment:
          self._open_attachment(attachment)

      self.push_screen(AttachmentMenu(item.attachments), handle_selection)

  def _open_attachment(self, attachment: Attachment) -> None:
    storage_base = Path("~/Zotero/storage").expanduser()
    full_path = attachment.get_absolute_path(storage_base)

    try:
      open_file(full_path)
      self.notify(f"Opening attachments for: {attachment.path.name}")
    except Exception as e:
      self.notify(str(e), severity="error")
