# agent/tools/rag_tool.py
from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional

from smolagents import Tool
from db.iris_client import IRISClient

_JSON = dict(indent=4, sort_keys=True, default=str)


# ----------------------------- Base class -----------------------------

class _BaseRAGSQLTool(Tool):
    """
    Base class that manages/reuses a single IRISClient connection.
    Computes query embeddings inside IRIS using EMBEDDING(text, '<config>').
    """

    def __init__(self, db: Optional[IRISClient] = None, embedding_config_env: str = "EMBEDDING_CONFIG_NAME") -> None:
        super().__init__()
        self._db = db
        self._embed_config = os.getenv(embedding_config_env, "my-openai-config")

    def setup(self) -> None:
        if self._db is None:
            self._db = IRISClient()

    def _ensure_connected(self) -> None:
        assert self._db is not None
        try:
            self._db.query_one("SELECT 1 AS one")
        except Exception:
            self._db = IRISClient()

    @staticmethod
    def _validate_config_name(name: str) -> str:
        """
        For safety, only allow [A-Za-z0-9._-] in the config name we inline in SQL.
        """
        if not re.fullmatch(r"[A-Za-z0-9._-]+", name or ""):
            raise ValueError(
                "Invalid EMBEDDING config name. Allowed: letters, digits, dot, underscore, dash."
            )
        return name


# --------------------------- Doc search tool ---------------------------

class RAGDocSearchTool(_BaseRAGSQLTool):
    """
    Semantic search over knowledge base documents:

    • Scores each DocVectors.Embedding against EMBEDDING(:query, '<config>') inside IRIS
    • Returns top-k snippets (DocID, Title, Body snippet, score)
    """

    name = "rag_doc_search"
    description = (
        "Semantic search over Docs that can be used to answer questions about customer support. "
        "Docs can include faq, manuals, policies, warranty, etc."
    )
    inputs: Dict[str, Dict[str, Any]] = {
        "query": {"type": "string", "description": "Natural-language query (required)."},
        "k": {"type": "integer", "description": "How many snippets to return (default 3, max 10).", "nullable": True},
    }
    output_type = "string"

    def forward(self, query: str, k: int = 3) -> str:
        self.setup()
        self._ensure_connected()
        assert self._db is not None

        q = (query or "").strip()
        if not q:
            return json.dumps({"snippets": [], "note": "empty query"}, **_JSON)

        top_k = max(1, min(int(k), 10))
        cfg = self._validate_config_name(self._embed_config)

        sql = f"""
        SELECT TOP {top_k}
            c.ChunkID            AS chunk_id,
            c.DocID              AS doc_id,
            c.Title              AS title,
            SUBSTRING(c.ChunkText, 1, 400) AS snippet,
            VECTOR_DOT_PRODUCT(c.Embedding, EMBEDDING(?, '{cfg}')) AS score
        FROM Agent_Data.DocChunks c
        ORDER BY score DESC
        """
        rows = self._db.query(sql, [q])

        payload = {
            "snippets": [
                {
                    "chunk_id": r.get("chunk_id"),
                    "doc_id": r.get("doc_id"),
                    "title": r.get("title"),
                    "snippet": (r.get("snippet") or "").strip(),
                    "score": float(r["score"]) if r.get("score") is not None else None,
                }
                for r in rows
            ]
        }
        return json.dumps(payload, **_JSON)


# ------------------------- Product search tool -------------------------

class RAGProductSearchTool(_BaseRAGSQLTool):
    """
    Semantic search over products:

    • Scores each ProductVectors.Embedding against EMBEDDING(:query, '<config>') in IRIS
    • Optional filters: price_max (<=)
    • Returns top-k products with similarity score
    """

    name = "rag_product_search"
    description = (
        "Semantic search over products names and descriptions. Optinally you can specify maximum price"
    )
    inputs: Dict[str, Dict[str, Any]] = {
        "query": {"type": "string", "description": "Natural-language query (required)."},
        "k": {"type": "integer", "description": "How many products to return (default 5, max 20).", "nullable": True},
        "price_max": {"type": "number", "description": "Optional maximum price.", "nullable": True},
    }
    output_type = "string"

    def forward(
        self,
        query: str,
        k: int = 5,
        price_max: Optional[float] = None,
    ) -> str:
        self.setup()
        self._ensure_connected()
        assert self._db is not None

        q = (query or "").strip()
        if not q:
            return json.dumps({"products": [], "note": "empty query"}, **_JSON)

        top_k = max(1, min(int(k), 20))
        cfg = self._validate_config_name(self._embed_config)

        # Build WHERE for optional filters (all bound as parameters)
        where = []
        params: List[Any] = [q]  # first param is the text for EMBEDDING(?, cfg)
        if price_max is not None and price_max >= 0:
            where.append("p.Price <= ?")
            params.append(price_max)
        where_sql = f"WHERE {' AND '.join(where)}" if where else ""

        sql = f"""
        SELECT TOP {top_k}
            p.ProductID,
            p.Name,
            p.Category,
            p.Price,
            VECTOR_DOT_PRODUCT(p.Embedding, EMBEDDING(?, '{cfg}')) score
        FROM Agent_Data.Products p
        {where_sql}
        ORDER BY score DESC
        """
        rows = self._db.query(sql, params)

        payload = {
            "products": [
                {
                    "ProductID": r.get("ProductID"),
                    "Name": r.get("Name"),
                    "Category": r.get("Category"),
                    "Price": r.get("Price"),
                    "score": float(r["score"]) if r.get("score") is not None else None,
                }
                for r in rows
            ]
        }
        return json.dumps(payload, **_JSON)


__all__ = [
    "RAGDocSearchTool",
    "RAGProductSearchTool",
]
