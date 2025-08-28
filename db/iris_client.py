# runtime/src/db/iris_client.py
from __future__ import annotations

from typing import Any, Iterable, List, Dict, Tuple, Optional

import os 

# InterSystems IRIS Python DB-API (PEP 249)
# Docs: https://docs.intersystems.com/iris20252/csp/docbook/DocBook.UI.Page.cls?KEY=BPYNAT_pyapi
import iris


# --- Get connection settings from environment ---
_HOST: str = os.getenv("IRIS_HOST", "localhost") 
_PORT: int = int(os.getenv("IRIS_PORT", 1972))
_NAMESPACE: str = os.getenv("IRIS_NAMESPACE", "USER")
_USERNAME: str = os.getenv("IRIS_USERNAME", "SuperUser") 
_PASSWORD: str = os.getenv("IRIS_PASSWORD", "SYS")
# -------------------------------------------------------------


class IRISClient:
    """
    Minimal wrapper around InterSystems IRIS DB-API connection.

    - Uses iris.connect(host, port, namespace, username, password)
    - Autocommit is enabled
    - Param placeholders are '?', e.g.: "SELECT * FROM T WHERE id = ?"
    """

    def __init__(
        self,
        host: str = _HOST,
        port: int = _PORT,
        namespace: str = _NAMESPACE,
        username: str = _USERNAME,
        password: str = _PASSWORD,
        autocommit: bool = True,
    ) -> None:
        self._conn = iris.connect(host, port, namespace, username, password)
        self._conn.autocommit = autocommit

    # --- Context manager support ---
    def __enter__(self) -> "IRISClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    # --- Public API ---
    def query(self, sql: str, params: Optional[Iterable[Any]] = None) -> List[Dict[str, Any]]:
        """
        Run a SELECT and return rows as a list of dicts.
        Use '?' placeholders in SQL and pass params as a sequence.
        """
        cur = self._conn.cursor()
        try:
            cur.execute(sql, tuple(params or ()))
            cols = [c[0] for c in (cur.description or [])]
            return [dict(zip(cols, row)) for row in cur.fetchall()]
        finally:
            cur.close()

    def query_one(self, sql: str, params: Optional[Iterable[Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Run a SELECT and return a single row as dict (or None).
        """
        cur = self._conn.cursor()
        try:
            cur.execute(sql, tuple(params or ()))
            cols = [c[0] for c in (cur.description or [])]
            row = cur.fetchone()
            return dict(zip(cols, row)) if row else None
        finally:
            cur.close()

    def execute(self, sql: str, params: Optional[Iterable[Any]] = None) -> int:
        """
        Run INSERT/UPDATE/DELETE. Returns rowcount.
        """
        cur = self._conn.cursor()
        try:
            cur.execute(sql, tuple(params or ()))
            return cur.rowcount if cur.rowcount is not None else 0
        finally:
            cur.close()

    def close(self) -> None:
        try:
            self._conn.close()
        except Exception:
            pass
