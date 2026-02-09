from dataclasses import dataclass, field
from pathlib import Path
import sqlite3


@dataclass(frozen=True)
class Attachment:
  path: Path
  item_key: str  # The 8-char folder name (e.g., 'A8JX7B2A')
  is_link: bool

  def get_absolute_path(self, storage_base: Path) -> Path:
    if not self.is_link:
      # Stored files look like 'storage:paper.pdf' in DB
      clean_name = str(self.path).replace("storage:", "")
      return storage_base / self.item_key / clean_name
    return self.path


@dataclass(frozen=True)
class Author:
  last_name: str
  first_name: str

  def __str__(self):
    return f"{self.last_name}, {self.first_name}"


@dataclass(frozen=True)
class ZoteroItem:
  item_id: int
  key: str
  title: str
  authors: list[Author]
  date: str
  # abstract: str
  attachments: list[Attachment] = field(default_factory=list)

  @property
  def author_summary(self) -> str:
    """Returns 'Smith et al.' or 'Smith' for the TUI table."""
    if not self.authors:
      return "Unknown"
    if len(self.authors) == 2:
      return f"{self.authors[0].last_name} and {self.authors[1].last_name}"
    if len(self.authors) > 1:
      return f"{self.authors[0].last_name} et al."

    return self.authors[0].last_name
