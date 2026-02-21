import bibtexparser

from dataclasses import dataclass, field
from pathlib import Path
from bibtexparser.bibdatabase import BibDatabase


class UnsupportedItemTypeError(Exception):
  """Raised when an item type is not yet mapped for BibTeX."""

  pass


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

  def __str__(self) -> str:
    # return f"{self.last_name}, {self.first_name}"
    return f"{self.first_name} {self.last_name}"

  @property
  def short_str(self) -> str:
    initials_list = [f"{s[0].upper()}." for s in self.first_name.split()]
    initials = " ".join(initials_list)
    return f"{initials} {self.last_name}"


@dataclass(frozen=True)
class ZoteroItem:
  item_id: int
  key: str
  item_type: str

  title: str
  authors: list[Author]
  year: int

  venue: str | None = None  # Publication, Proceedings, or Book Title
  volume: str | None = None
  issue: str | None = None
  pages: str | None = None
  doi: str | None = None
  publisher: str | None = None
  # abstract: str

  abstract: str | None = None
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

  @property
  def author_full(self) -> str:
    if not self.authors:
      return "Unknown"

    return "; ".join([str(author) for author in self.authors])

  def is_query_match(self, query: str) -> bool:
    if not query:
      return True

    query = query.lower()

    if query in self.title.lower():
      return True

    for author in self.authors:
      if (
        query in author.first_name.lower()
        or query in author.last_name.lower()
        or query in author.short_str.lower()
      ):
        return True

    return False

  def to_bibtex(self) -> str:
    # Strict mapping requirement
    type_map = {
      "conferencePaper": "inproceedings",
      "journalArticle": "article",
      "preprint": "article",  # BibLaTeX standard for preprints/arxiv
      "book": "book",
      "bookSection": "incollection",
    }

    if self.item_type not in type_map:
      raise UnsupportedItemTypeError(f"Type '{self.item_type}' not supported yet.")

    # Construct BibDatabase object
    db = BibDatabase()
    author_last = (
      self.authors[0].last_name.lower().replace(" ", "") if self.authors else "anon"
    )

    entry = {
      "ID": f"{author_last}{self.year}",
      "ENTRYTYPE": type_map[self.item_type],
      "title": self.title,
      "author": " and ".join([str(a) for a in self.authors]),
      "year": str(self.year),
    }

    # Context-aware field mapping
    if self.venue:
      if self.item_type in ["journalArticle", "bookSection"]:
        entry["journal"] = self.venue
      elif self.item_type in ["conferencePaper", "preprint"]:
        entry["booktitle"] = self.venue

    if self.doi:
      entry["doi"] = self.doi
    if self.pages:
      entry["pages"] = self.pages
    if self.volume:
      entry["volume"] = self.volume
    if self.publisher:
      entry["publisher"] = self.publisher

    db.entries = [entry]
    return bibtexparser.dumps(db).strip()
