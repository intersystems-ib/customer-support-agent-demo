# scripts/embed_sql.py
from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

from dotenv import load_dotenv
load_dotenv()

# allow: python scripts/embed_sql.py  (from repo root)
if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, os.path.abspath("."))

from db.iris_client import IRISClient


# --------------------------- Config ---------------------------

DOCS_DIR = Path(os.getenv("DOCS_DIR", "iris/docs"))
EMBEDDING_CONFIG = os.getenv("EMBEDDING_CONFIG_NAME", "my-openai-config")
DOC_BODY_MAX_CHARS = int(os.getenv("DOC_BODY_MAX_CHARS", "4000"))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))
SUPPORTED_EXTS = {".md", ".markdown", ".txt"}

# Rebuild flags
REFRESH_DOC_CHUNK_VECTORS = os.getenv("REFRESH_DOC_CHUNK_VECTORS", "1") == "1"
REFRESH_PRODUCT_VECTORS   = os.getenv("REFRESH_PRODUCT_VECTORS", "1") == "1"

def _validate_config_name(name: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9._-]+", name or ""):
        raise ValueError("Invalid EMBEDDING config name. Allowed: letters, digits, dot, underscore, dash.")
    return name


# ------------------------- File loading ------------------------

def _read_docs_from_fs(root: Path) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    if not root.exists():
        print(f"[warn] docs dir not found: {root.resolve()}")
        return rows

    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED_EXTS:
            continue

        doc_id = path.stem
        text = path.read_text(encoding="utf-8", errors="ignore").strip()

        # Title = first Markdown heading if present, else filename
        title = path.stem
        for line in text.splitlines():
            if line.strip().startswith("#"):
                title = line.lstrip("#").strip() or title
                break

        body = text
        if body.startswith("#") and title in body[: len(title) + 4]:
            body = "\n".join(body.splitlines()[1:]).lstrip()

        if len(body) > DOC_BODY_MAX_CHARS:
            body = body[: DOC_BODY_MAX_CHARS]

        rows.append({"DocID": doc_id, "Title": title, "Body": body})
    return rows


# --------------------------- Chunking --------------------------

def make_chunks(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[Tuple[int, int, str]]:
    if size <= 0:
        return [(0, len(text), text)]
    step = max(1, size - max(0, overlap))
    out: List[Tuple[int, int, str]] = []
    i = 0
    while i < len(text):
        chunk = text[i : i + size]
        if not chunk:
            break
        out.append((i, i + len(chunk), chunk))
        i += step
    return out


# --------------------------- DB ops ---------------------------

def upsert_doc_chunks(db: IRISClient, doc_id: str, title: str, body: str) -> int:
    """Upsert chunks into Agent_Data.DocChunks using (DocID, ChunkIndex) as natural key."""
    chunks = make_chunks(body)
    count = 0
    for idx, (start, end, chunk) in enumerate(chunks):
        # Upsert via INSERT OR UPDATE using the UNIQUE (DocID, ChunkIndex)
        db.execute(
            """
            INSERT OR UPDATE Agent_Data.DocChunks
                (DocID, ChunkIndex, StartPos, EndPos, Title, Heading, ChunkText)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [doc_id, idx, start, end, title, None, chunk],
        )
        count += 1
    return count


def rebuild_doc_chunk_vectors(db: IRISClient, config: str) -> None:
    cfg = _validate_config_name(config)
    # Rebuild all (simple & deterministic). Change to WHERE Embedding IS NULL for incremental.
    db.execute(
        f"""
        UPDATE Agent_Data.DocChunks c
        SET Embedding = EMBEDDING(c.ChunkText, '{cfg}')
        """
    )


def rebuild_product_vectors(db: IRISClient, config: str) -> None:
    cfg = _validate_config_name(config)
    db.execute(
        f"""
        UPDATE Agent_Data.Products p
        SET Embedding = EMBEDDING(p.Name || ' ' || COALESCE(p.Description,''), '{cfg}')
        """
    )


# ---------------------------- Main ----------------------------

def main() -> int:
    print(f"[info] docs dir           : {DOCS_DIR.resolve()}")
    print(f"[info] embedding config   : {EMBEDDING_CONFIG}")
    print(f"[info] chunk size/overlap : {CHUNK_SIZE}/{CHUNK_OVERLAP}")

    db = IRISClient()

    # 1) Load & chunk files → upsert into DocChunks
    docs = _read_docs_from_fs(DOCS_DIR)
    total_chunks = 0
    for d in docs:
        total_chunks += upsert_doc_chunks(db, d["DocID"], d["Title"], d["Body"])
    print(f"[ok] upserted {total_chunks} chunks across {len(docs)} docs")

    # 2) Build vectors inside IRIS
    if REFRESH_DOC_CHUNK_VECTORS:
        print("[info] rebuilding DocChunks.Embedding via EMBEDDING() …")
        rebuild_doc_chunk_vectors(db, EMBEDDING_CONFIG)
        print("[ok] DocChunks vectors updated")

    if REFRESH_PRODUCT_VECTORS:
        print("[info] rebuilding Products.Embedding via EMBEDDING() …")
        rebuild_product_vectors(db, EMBEDDING_CONFIG)
        print("[ok] Products vectors updated")

    # 3) Quick sanity checks
    try:
        c1 = db.query_one("SELECT COUNT(*) AS n FROM Agent_Data.DocChunks") or {}
        c2 = db.query_one("SELECT COUNT(*) AS n FROM Agent_Data.Products WHERE Embedding IS NOT NULL") or {}
        print(f"[info] DocChunks rows      : {c1.get('n')}")
        print(f"[info] Products embedded  : {c2.get('n')}")
    except Exception:
        pass

    print("[done]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())