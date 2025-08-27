# runtime/src/agent/tools/sql_tool.py
from __future__ import annotations

import json
from typing import Any, Dict, Optional, List

from smolagents import Tool
from db.iris_client import IRISClient

_JSON_KW = dict(indent=4, sort_keys=True, default=str)


class _BaseSQLTool(Tool):
    """
    Base class that manages/reuses a single IRISClient connection.
    Pass a shared IRISClient(db) if you want multiple tools to reuse it.
    """

    def __init__(self, db: Optional[IRISClient] = None) -> None:
        super().__init__()
        self._db = db

    def setup(self) -> None:
        """Lazy init if no client was injected."""
        if self._db is None:
            self._db = IRISClient()

    def _ensure_connected(self) -> None:
        """Lightweight healthcheck; reconnect if needed."""
        assert self._db is not None
        try:
            self._db.query_one("SELECT 1 AS one")
        except Exception:
            self._db = IRISClient()

    # Helper shared across tools
    def _get_customer_id(self, email: str) -> Optional[int]:
        row = self._db.query_one(  # type: ignore[union-attr]
            "SELECT CustomerID FROM Agent_Data.Customers WHERE Email = ?",
            [email],
        )
        return int(row["CustomerID"]) if row and "CustomerID" in row else None


class SQLLastOrdersTool(_BaseSQLTool):
    """
    Return the most recent orders for a user (by email), limited by `limit`.
    Uses explicit SQL JOINs with Products and Shipments and IRIS SQL LIMIT.
    """

    name = "sql_last_orders"
    description = "Return the most recent orders for a user (by email). Uses explicit JOINs and LIMIT."
    inputs = {
        "user_email": {
            "type": "string", 
            "description": "Customer email (required)."
        },
        "limit": {
            "type": "integer", 
            "description": "Max rows to return (default 3).", 
            "nullable": True
        },
    }
    output_type = "string"

    def forward(self, user_email: str, limit: int = 30) -> str:
        self.setup()
        self._ensure_connected()
        assert self._db is not None

        cid = self._get_customer_id(user_email)
        if cid is None:
            return json.dumps({"orders": [], "note": "unknown user_email"}, **_JSON_KW)

        sql = f"""
        SELECT
            o.OrderID,
            o.OrderDate,
            o.Status,
            p.ProductID,
            p.Name     AS ProductName,
            p.Category AS Category,
            p.Price    AS Price,
            s.TrackingCode
        FROM Agent_Data.Orders AS o
        JOIN Agent_Data.Products  AS p ON p.ProductID = o.ProductID
        LEFT JOIN Agent_Data.Shipments AS s ON s.OrderID = o.OrderID
        WHERE o.CustomerID = ?
        ORDER BY o.OrderDate DESC
        LIMIT {int(max(1, limit))}
        """
        rows = self._db.query(sql, [cid])
        return json.dumps({"orders": rows}, **_JSON_KW)


class SQLOrderByIdTool(_BaseSQLTool):
    """
    Return details for a specific order **only if** it belongs to the given user (by email).
    Explicit JOINs for clarity.
    """

    name = "sql_order_by_id"
    description = "Return details for an order if it belongs to the given user (email)."
    inputs = {
        "user_email": {
            "type": "string", 
            "description": "Customer email (required)."
        },
        "order_id": {
            "type": "integer", 
            "description": "OrderID (required)."
        },
    }
    output_type = "string"

    def forward(self, user_email: str, order_id: int) -> str:
        self.setup()
        self._ensure_connected()
        assert self._db is not None

        cid = self._get_customer_id(user_email)
        if cid is None:
            return json.dumps({"order": None, "note": "unknown user_email"}, **_JSON_KW)

        sql = """
        SELECT
            o.OrderID,
            o.OrderDate,
            o.Status,
            p.ProductID,
            p.Name     AS ProductName,
            p.Category AS Category,
            p.Price    AS Price,
            s.TrackingCode
        FROM Agent_Data.Orders AS o
        JOIN Agent_Data.Products  AS p ON p.ProductID = o.ProductID
        LEFT JOIN Agent_Data.Shipments AS s ON s.OrderID = o.OrderID
        WHERE o.CustomerID = ? AND o.OrderID = ?
        """
        row = self._db.query_one(sql, [cid, int(order_id)])
        if not row:
            return json.dumps({"order": None, "note": "order not found or not owned by this user"}, **_JSON_KW)
        return json.dumps({"order": row}, **_JSON_KW)


class SQLOrdersInRangeTool(_BaseSQLTool):
    """
    Return all orders for a user in the inclusive date range [start_date, end_date] (YYYY-MM-DD).
    Explicit JOINs with Products and Shipments.
    """

    name = "sql_orders_in_range"
    description = "Return orders for a user (email) in the date range [start_date, end_date] (YYYY-MM-DD)."
    inputs: Dict[str, Dict[str, Any]] = {
        "user_email": {
            "type": "string", 
            "description": "Customer email (required)."
        },
        "start_date": {
            "type": "string", 
            "description": "Start date in 'YYYY-MM-DD' (required)."
        },
        "end_date": {
            "type": "string", 
            "description": "End date in 'YYYY-MM-DD' (required)."
        },
    }
    output_type = "string"

    def forward(self, user_email: str, start_date: str, end_date: str) -> str:
        self.setup()
        self._ensure_connected()
        assert self._db is not None

        cid = self._get_customer_id(user_email)
        if cid is None:
            return json.dumps({"orders": [], "note": "unknown user_email"}, **_JSON_KW)

        sql = """
        SELECT
            o.OrderID,
            o.OrderDate,
            o.Status,
            p.ProductID,
            p.Name     AS ProductName,
            p.Category AS Category,
            p.Price    AS Price,
            s.TrackingCode
        FROM Agent_Data.Orders AS o
        JOIN Agent_Data.Products  AS p ON p.ProductID = o.ProductID
        LEFT JOIN Agent_Data.Shipments AS s ON s.OrderID = o.OrderID
        WHERE o.CustomerID = ?
          AND o.OrderDate BETWEEN TO_DATE(?, 'YYYY-MM-DD') AND TO_DATE(?, 'YYYY-MM-DD')
        ORDER BY o.OrderDate DESC
        """
        rows = self._db.query(sql, [cid, start_date, end_date])
        return json.dumps({"orders": rows}, **_JSON_KW)


__all__ = ["SQLLastOrdersTool", "SQLOrderByIdTool", "SQLOrdersInRangeTool"]
