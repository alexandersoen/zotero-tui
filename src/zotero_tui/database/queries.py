from pathlib import Path
import sqlite3
from zotero_tui.database.models import ZoteroItem, Attachment, Author


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


def fetch_all_items(conn: sqlite3.Connection):
  """Generates ZoteroItem objects by orchestrating helper functions."""
  # Main metadata query
  #      MAX(CASE WHEN f.fieldName = 'abstractNote' THEN idv.value END) as abstract,
  query = """
    SELECT 
        i.itemID, i.key,
        MAX(CASE WHEN f.fieldName = 'title' THEN idv.value END) as title,
        MAX(CASE WHEN f.fieldName = 'date' THEN idv.value END) as date
    FROM items i
    LEFT JOIN itemData id ON i.itemID = id.itemID
    LEFT JOIN fields f ON id.fieldID = f.fieldID
    LEFT JOIN itemDataValues idv ON id.valueID = idv.valueID
    WHERE i.itemID NOT IN (SELECT itemID FROM deletedItems)  -- Filter Trash
      AND i.itemTypeID NOT IN (
        3,  -- Attachment
        14, -- Document
        28  -- Note
      )
    GROUP BY i.itemID
    """

  for row in conn.execute(query):
    item_id = row["itemID"]

    yield ZoteroItem(
      item_id=item_id,
      key=row["key"],
      title=row["title"] or "Untitled",
      authors=fetch_authors_for_item(conn, item_id),
      date=row["date"] or "",
      # abstract=row["abstract"] or "",
      attachments=fetch_attachments_for_item(conn, item_id),
    )
