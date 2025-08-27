# python/src/agent/customer_support_agent.py
from __future__ import annotations

import os
from typing import Dict, Any

from smolagents import CodeAgent, OpenAIServerModel

# Fixed tools (ensure each tool has a good docstring so smolagents can auto-describe it)
from agent.tools.sql_tool import SQLLastOrdersTool, SQLOrderByIdTool, SQLOrdersInRangeTool
from .tools.rag_tool import RAGDocSearchTool, RAGProductSearchTool
from .tools.shipping_tool import ShippingStatusTool

from db.iris_client import IRISClient


class CustomerSupportAgent:
    """
    Minimal Customer Support agent using smolagents.CodeAgent.
    - OPENAI_API_KEY must be set in the environment.
    - Tools are fixed (SQLTool, RAGTool, ShippingTool).
    - We rely on smolagents' default system prompt and tool auto-documentation.
    """

    def __init__(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required in environment.")

        model_id = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.2"))
        max_steps = int(os.getenv("AGENT_MAX_STEPS", "8"))
        verbosity = int(os.getenv("AGENT_VERBOSITY", "1"))  # 0,1,2

        model = OpenAIServerModel(
            model_id=model_id,
            api_key=api_key,
            temperature=temperature,
            max_tokens=4096
        )

        # Fixed toolset

        iris_client = IRISClient()
        sql_last_order_tool = SQLLastOrdersTool(db=iris_client) 
        sql_order_by_id_tool = SQLOrderByIdTool(db=iris_client)
        sql_orders_in_range_tool = SQLOrdersInRangeTool(db=iris_client)
        rag_doc_search_tool = RAGDocSearchTool(db=iris_client)
        rag_product_search_tool = RAGProductSearchTool(db=iris_client)
        shipping_status_tool = ShippingStatusTool()

        # Let smolagents use its default system prompt and auto-describe tools from docstrings
        self.agent = CodeAgent(
            tools=[sql_last_order_tool, sql_order_by_id_tool, sql_orders_in_range_tool, rag_doc_search_tool, rag_product_search_tool, shipping_status_tool],
            model=model,
            max_steps=max_steps,
            verbosity_level=verbosity,
        )

    @staticmethod
    def _compose_task(user_email: str, message: str) -> str:
        """
        Build the user task. Keep guidance minimal; do not duplicate tool descriptions here.
        """
        return (
            f"User email: {user_email}\n"
            f"User message: {message}\n\n"
            "If the user asks about where is an order, try to find the location of the shipment."
            "Security rule: Only reveal order or personal information if it belongs to this email. If you cannot verify ownership, refuse to answer.\n"
            "Answer concisely and ground your response only on tool outputs."
            "Format your final answer in nice markdown"
        )

    def run(self, user_email: str, message: str) -> Dict[str, Any]:
        task = self._compose_task(user_email, message)
        answer = self.agent.run(task)
        return {"answer": answer}

    def __call__(self, user_email: str, message: str) -> Dict[str, Any]:
        return self.run(user_email=user_email, message=message)
