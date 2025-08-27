# scripts/embed_sql.py
from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import Dict, List

from dotenv import load_dotenv
load_dotenv()

# allow: python scripts/embed_sql.py  (from repo root)
if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, os.path.abspath("."))

from db.iris_client import IRISClient  # noqa: E402


# --------------------------- Config ---------------------------

DOCS_DIR = Path(os.getenv("DOCS_DIR", "iris/docs"))
EMBEDDING_CONFIG = os.getenv("EMBEDDING_CONFIG_NAME", "my-openai-config")
DOC_BODY_MAX_CHARS = int(os.getenv("DOC_BODY_MAX_CHARS", "4000"))  # matches schema
SUPPORTED_EXTS = {".md", ".markdown", ".txt"}


def _validate_config_name(name: str) -> str:
    """Allow only safe characters for inlining into SQL."""
    if not re.fullmatch(r"[A-Za-z0-9._-]+", name or ""):
        raise ValueError("Invalid EMBEDDING config name. Allowed: letters, digits, dot, underscore, dash.")
    return name


# ------------------------- File loading ------------------------

def _read_docs_from_fs(root: Path) -> List[Dict[str, str]]:
    """
    Walk the docs folder and return rows: {DocID, Title, BodyText, DocType}
    - DocID: filename (without extension)
    - Title: first Markdown heading if present, else filename
    - BodyText: file content (first H1 dropped), truncated to DOC_BODY_MAX_CHARS
    """
    rows: List[Dict[str, str]] = []
    if not root.exists():
        print(f"[warn] docs dir not found: {root.resolve()}")
        return rows

    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED_EXTS:
            continue

        doc_id = path.stem
        text = path.read_text(encoding="utf-8", errors="ignore").strip()

        # Title = first '#' heading if present
        title = path.stem
        for line in text.splitlines():
            if line.strip().startswith("#"):
                title = line.lstrip("#").strip() or title
                break

        # Drop first heading line from body if it matches title
        body = text
        if body.startswith("#") and title in body[: len(title) + 4]:
            body = "\n".join(body.splitlines()[1:]).lstrip()

        if len(body) > DOC_BODY_MAX_CHARS:
            body = body[: DOC_BODY_MAX_CHARS]

        rows.append(
            {
                "DocID": doc_id,
                "Title": title,
                "BodyText": body,
                "DocType": path.suffix.lstrip(".").upper(),
            }
        )
    return rows


# --------------------------- DB ops ---------------------------

def upsert_docs(db: IRISClient, docs: List[Dict[str, str]]) -> int:
    """
    Upsert docs using IRIS 'INSERT OR UPDATE' so PK collisions update rows.
    """
    n = 0
    for r in docs:
        db.execute(
            """
            INSERT OR UPDATE Agent_Data.Docs (DocID, Title, BodyText, DocType)
            VALUES (?, ?, ?, ?)
            """,
            [r["DocID"], r["Title"], r["BodyText"], r["DocType"]],
        )
        n += 1
    return n


def rebuild_doc_vectors(db: IRISClient, config: str) -> None:
    """
    Use IRIS EMBEDDING() to (re)build vectors in Agent_Data.DocVectors.
    """
    cfg = _validate_config_name(config)
    sql = f"""
    INSERT OR UPDATE Agent_Data.DocVectors (DocID, Embedding)
    SELECT
      d.DocID,
      EMBEDDING(COALESCE(d.Title,'') || CHAR(10) || CHAR(10) || COALESCE(d.BodyText,''), '{cfg}')
    FROM Agent_Data.Docs AS d
    """
    db.execute(sql)


def rebuild_product_vectors(db: IRISClient, config: str) -> None:
    """
    Use IRIS EMBEDDING() to (re)build vectors in Agent_Data.ProductVectors.
    Text = Products.Name + ' ' + Products.Description
    """
    cfg = _validate_config_name(config)
    sql = f"""
    INSERT OR UPDATE Agent_Data.ProductVectors (ProductID, Embedding)
    SELECT
      p.ProductID,
      EMBEDDING(p.Name || ' ' || COALESCE(p.Description,''), '{cfg}')
    FROM Agent_Data.Products AS p
    """
    db.execute(sql)


# ---------------------------- Main ----------------------------

def main() -> int:
    print(f"[info] docs dir         : {DOCS_DIR.resolve()}")
    print(f"[info] embedding config : {EMBEDDING_CONFIG}")

    db = IRISClient()  # hardcoded connector

    # 1) Load/refresh docs from the filesystem
    docs = _read_docs_from_fs(DOCS_DIR)
    if docs:
        n = upsert_docs(db, docs)
        print(f"[ok] upserted docs     : {n}")
    else:
        print("[warn] no docs found on disk to load")

    # 2) Rebuild vectors via EMBEDDING() (inside IRIS)
    print("[info] rebuilding DocVectors via EMBEDDING() …")
    rebuild_doc_vectors(db, EMBEDDING_CONFIG)
    print("[ok] DocVectors updated")

    print("[info] rebuilding ProductVectors via EMBEDDING() …")
    rebuild_product_vectors(db, EMBEDDING_CONFIG)
    print("[ok] ProductVectors updated")

    # (optional) Quick sanity checks
    try:
        c1 = db.query_one("SELECT COUNT(*) AS n FROM Agent_Data.DocVectors") or {}
        c2 = db.query_one("SELECT COUNT(*) AS n FROM Agent_Data.ProductVectors") or {}
        print(f"[info] DocVectors rows  : {c1.get('n')}")
        print(f"[info] ProductVectors rows: {c2.get('n')}")
    except Exception:
        pass

    print("[done]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
