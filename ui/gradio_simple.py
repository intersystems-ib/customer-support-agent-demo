# ui/gradio_simple.py
from __future__ import annotations
import os
import gradio as gr
from agent.customer_support_agent import CustomerSupportAgent

from dotenv import load_dotenv
load_dotenv()

_AGENT: CustomerSupportAgent | None = None
def _agent() -> CustomerSupportAgent:
    global _AGENT
    if _AGENT is None:
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY is not set.")
        _AGENT = CustomerSupportAgent()
    return _AGENT

def respond(message: str, history: list[tuple[str, str]], email: str) -> str:
    if not email or "@" not in email:
        return "Please enter a valid email (e.g., alice@example.com)."
    return _agent()(user_email=email, message=message)["answer"]

def main():
    email_box = gr.Textbox(label="Email", value="alice@example.com", placeholder="you@example.com")
    demo = gr.ChatInterface(
        fn=respond,
        additional_inputs=[email_box],
        title="🛍️ Customer Support Agent (IRIS + smolagents)",
        description="Ask about your orders, shipping, returns, or warranty.",
        textbox=gr.Textbox(placeholder="Type your question…", autofocus=True),
        chatbot=gr.Chatbot(height=420),  # optional; safe across versions
    )
    demo.launch(server_name="0.0.0.0", server_port=int(os.getenv("PORT", "7860")), share=False)

if __name__ == "__main__":
    main()