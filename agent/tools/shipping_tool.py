# agent/tools/shipping_tool.py
from __future__ import annotations

import json
import os
import uuid
from typing import Any, Dict, Optional

import requests
from smolagents import Tool

_JSON = dict(indent=4, sort_keys=True, default=str)


class ShippingStatusTool(Tool):
    """
    Send shipping status payloads to the IRIS REST endpoint and return the JSON response.

    Default endpoint: http://localhost:52773/api/shipping/status
    (Override with env IRIS_SHIPPING_STATUS_URL if you need to.)

    Example payload sent:
      {"orderStatus": "Processing", "trackingNumber": "DHL7788"}

    Headers include:
      X-Request-Id: <uuid if not provided>
    """

    name = "shipping_status"
    description = (
        "Returns shipping status information of an order by providing its status and tracking number."
        "It helps to track the shipment and get updates on its progress and location."
        "It returns information like carrier, status, ETA and timeline events with locations."
        "It also returns trace information like InterSystems IRIS SessionId and URL to view full trace of request."
    )
    inputs = {
        "order_status": {"type": "string", "description": "Order status to report (e.g., 'Processing')."},
        "tracking_number": {"type": "string", "description": "Tracking number (e.g., 'DHL7788')."},
        "request_id": {"type": "string", "description": "Optional request id for tracing. If omitted, a UUID is generated.", "nullable": True},
        "url": {"type": "string", "description": "Optional override for the IRIS endpoint URL.", "nullable": True},
        "timeout_sec": {"type": "number", "description": "Optional HTTP timeout (seconds). Default 10.", "nullable": True},
    }
    output_type = "string"

    def __init__(self) -> None:
        super().__init__()
        self.default_url = os.getenv(
            "IRIS_SHIPPING_STATUS_URL",
            "http://localhost:52773/api/shipping/status",
        )

    def forward(
        self,
        order_status: str,
        tracking_number: str,
        request_id: Optional[str] = None,
        url: Optional[str] = None,
        timeout_sec: float = 10.0,
    ) -> str:
        endpoint = (url or self.default_url).rstrip("/")
        rid = request_id or str(uuid.uuid4())

        payload: Dict[str, Any] = {
            "orderStatus": order_status,
            "trackingNumber": tracking_number,
        }
        headers = {
            "Content-Type": "application/json",
            "X-Request-Id": rid,
        }

        try:
            resp = requests.post(endpoint, json=payload, headers=headers, timeout=timeout_sec)
            content_type = resp.headers.get("content-type", "")
            # Try to return server JSON if possible; otherwise wrap text
            if "application/json" in content_type.lower():
                data = resp.json()
            else:
                data = {"status": resp.status_code, "body": resp.text}

            # Always include request/trace info in the tool's return
            wrapped = {
                "endpoint": endpoint,
                "requestId": rid,
                "httpStatus": resp.status_code,
                "response": data,
            }
            return json.dumps(wrapped, **_JSON)
        except Exception as e:
            return json.dumps(
                {
                    "endpoint": endpoint,
                    "requestId": rid,
                    "error": f"{type(e).__name__}: {e}",
                },
                **_JSON,
            )
