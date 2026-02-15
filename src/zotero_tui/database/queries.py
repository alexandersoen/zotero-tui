import json
import sqlite3

from collections import defaultdict
from pathlib import Path
from typing import NamedTuple
from zotero_tui.database.models import ZoteroItem, Attachment, Author


class EntryKey(NamedTuple):
  item_id: int
  item_key: str
  item_type: str


def fetch_authors_for_item(conn: sqlite3.Connection, item_id: int) -> list[Author]:
  """Retrieves a sorted list of authors for a specific item ID."""
  query = """
    SELECT c.lastName, c.firstName
    FROM itemCreators ic
    JOIN creators c ON ic.creatorID = c.creatorID
    WHERE ic.itemID = ?
    ORDER BY ic.orderIndex
    """
  return [
    Author(last_name=row["lastName"], first_name=row["firstName"])
    for row in conn.execute(query, (item_id,))
  ]


def fetch_attachments_for_item(
  conn: sqlite3.Connection, item_id: int
) -> list[Attachment]:
  """Retrieves all file attachments linked to a parent item."""
  query = """
    SELECT path, key 
    FROM itemAttachments 
    JOIN items USING (itemID) 
    WHERE parentItemID = ?
    """
  attachments = []
  for row in conn.execute(query, (item_id,)):
    if row["path"]:
      p = Path(row["path"])
      attachments.append(
        Attachment(
          path=p, item_key=row["key"], is_link=not str(p).startswith("storage:")
        )
      )
  return attachments


def get_venue_str(meta: dict[str, str]) -> str | None:
  key_order = [
    "proceedingsTitle",
    "series",
    "publicationTitle",
    "bookTitle",  # For book sections (venue is the book)
    # Secondary fallbacks
    "conferenceName",
    "journalAbbreviation",
    "repository",  # For arXiv
  ]

  if meta.get("repository") == "arXiv":
    arxiv_id = ""
    if "DOI" in meta:
      arxiv_id = meta["DOI"].split("/")[1]
      arxiv_id = arxiv_id.replace(".", ":", 1)
    elif "extra" in meta:
      arxiv_id = meta["extra"].split(" ")[0]
    elif "archiveID" in meta:
      arxiv_id = meta["archiveID"]

    return f"arXiv preprint {arxiv_id}".strip()

  for key in key_order:
    if key in meta:
      return meta[key]

  return None


def fetch_all_items(conn: sqlite3.Connection):
  """Generates ZoteroItem objects by orchestrating helper functions."""
  # Main metadata query
  ignore_fields = {"abstractNote", "accessDate", "libraryCatalog", "language"}
  query = """
    SELECT 
        i.itemID,
        i.key,
        it.typeName,
        f.fieldName,
        iv.value
    FROM items i
    JOIN itemTypes it ON i.itemTypeID = it.itemTypeID
    JOIN itemData id ON i.itemID = id.itemID
    JOIN fields f ON id.fieldID = f.fieldID
    JOIN itemDataValues iv ON id.valueID = iv.valueID
    WHERE i.itemID NOT IN (SELECT itemID FROM deletedItems)  -- Filter Trash
      AND i.itemTypeID NOT IN (
        3,  -- Attachment
        14, -- Document
        28  -- Note
      )
  """
  data: dict[EntryKey, dict[str, str]] = defaultdict(dict)
  for row in conn.execute(query):
    key = EntryKey(row["itemID"], row["key"], row["typeName"])
    field = row["fieldName"]
    value = row["value"]

    if field in ignore_fields:
      continue

    data[key][field] = value

  for key, meta in data.items():
    year = int(meta["date"][:4])

    yield ZoteroItem(
      # Keys
      item_id=key.item_id,
      key=key.item_key,
      item_type=key.item_type,
      # Main fields
      title=meta["title"],
      authors=fetch_authors_for_item(conn, key.item_id),
      year=year or 0,
      attachments=fetch_attachments_for_item(conn, key.item_id),
      # Meta
      venue=get_venue_str(meta),
      volume=meta.get("volume"),
      issue=meta.get("issue"),
      pages=meta.get("pages"),
      doi=meta.get("DOI"),
      publisher=meta.get("publisher"),
    )
