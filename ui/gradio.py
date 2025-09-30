# ui/gradio.py
from __future__ import annotations
import os
import io
import re
import contextlib
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

def format_debug_output(debug_text: str) -> str:
    """Format debug output with colors and structure using HTML/CSS"""
    if not debug_text.strip():
        return '<div style="color: #666; font-style: italic;">No debug information available.</div>'
    
    # Split into lines and process
    lines = debug_text.split('\n')
    formatted_lines = ['<div style="font-family: monospace; line-height: 1.6;">']
    
    in_code_block = False
    
    for line in lines:
        original_line = line
        line = line.strip()
        
        if not line:
            formatted_lines.append('<br>')
            continue
        
        # Handle code blocks
        if line.startswith('```'):
            if in_code_block:
                formatted_lines.append('</pre>')
                in_code_block = False
            else:
                formatted_lines.append('<pre style="background: #1e1e1e; color: #d4d4d4; padding: 12px; border-radius: 4px; margin: 8px 0; overflow-x: auto;">')
                in_code_block = True
            continue
        
        if in_code_block:
            # Inside code block - preserve formatting and add syntax highlighting
            escaped_line = original_line.replace('<', '&lt;').replace('>', '&gt;')
            # Basic Python syntax highlighting
            escaped_line = re.sub(r'\b(def|class|import|from|return|if|else|elif|for|while|try|except|with|as)\b', 
                                r'<span style="color: #569cd6;">\1</span>', escaped_line)
            escaped_line = re.sub(r'(\d+)', r'<span style="color: #b5cea8;">\1</span>', escaped_line)
            escaped_line = re.sub(r'(["\'])([^"\']*)\1', r'<span style="color: #ce9178;">\1\2\1</span>', escaped_line)
            formatted_lines.append(escaped_line)
            continue
        
        # Outside code blocks - format different types of output
        if 'Step' in line and (':' in line or 'step' in line.lower()):
            # Agent steps
            formatted_lines.append(f'<div style="color: #2196F3; font-weight: bold; margin: 8px 0; padding: 4px; border-left: 3px solid #2196F3; padding-left: 8px;">🔄 {line}</div>')
        elif 'Tool:' in line or 'calling tool' in line.lower() or 'using tool' in line.lower():
            # Tool calls
            formatted_lines.append(f'<div style="color: #4CAF50; font-weight: bold; padding: 4px; border-left: 3px solid #4CAF50; padding-left: 8px;">🔧 {line}</div>')
        elif 'error' in line.lower() or 'exception' in line.lower() or 'failed' in line.lower():
            # Errors
            formatted_lines.append(f'<div style="color: #F44336; font-weight: bold; padding: 4px; border-left: 3px solid #F44336; padding-left: 8px;">❌ {line}</div>')
        elif 'result' in line.lower() or 'output' in line.lower() or 'response' in line.lower():
            # Results
            formatted_lines.append(f'<div style="color: #9C27B0; padding: 4px; border-left: 3px solid #9C27B0; padding-left: 8px;">📊 {line}</div>')
        elif 'thinking' in line.lower() or 'reasoning' in line.lower():
            # Agent thinking
            formatted_lines.append(f'<div style="color: #FF9800; font-style: italic; padding: 4px;">💭 {line}</div>')
        else:
            # Regular text
            formatted_lines.append(f'<div style="color: #333; padding: 2px;">{line}</div>')
    
    if in_code_block:
        formatted_lines.append('</pre>')
    
    formatted_lines.append('</div>')
    return ''.join(formatted_lines)

def respond_with_debug(message: str, email: str):
    if not email or "@" not in email:
        return "Please enter a valid email (e.g., alice@example.com).", ""
    
    # Always capture debug output
    debug_output = io.StringIO()
    with contextlib.redirect_stdout(debug_output), contextlib.redirect_stderr(debug_output):
        answer = _agent()(user_email=email, message=message)["answer"]
    
    debug_text = debug_output.getvalue()
    formatted_debug = format_debug_output(debug_text)
    return answer, formatted_debug

def main():
    # Sample prompts for users to try
    SAMPLE_PROMPTS = [
        "Where is my order #1001?",
        "Show me my recent orders",
        "Find headphones under $120 with noise cancellation",
        "What's the return policy for electronics?",
        "Was my headphones order delivered?",
        "Show me electronics good for travel",
        "What warranty coverage do I have?",
        "If my order is out of warranty, what options do I have?",
        "Show me orders from last month"
    ]
    
    # Custom CSS for better debug formatting and prompt buttons
    custom_css = """
    .debug-container {
        max-height: 500px;
        overflow-y: auto;
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 16px;
        font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
        font-size: 14px;
        line-height: 1.4;
    }
    .debug-container div {
        margin: 2px 0;
    }
    .prompt-button {
        margin: 4px 2px;
        padding: 8px 12px;
        border-radius: 20px;
        font-size: 13px;
        background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .prompt-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    """
    
    with gr.Blocks(title="Customer Support Agent", css=custom_css) as demo:
        gr.Markdown("# 🛍️ Customer Support Agent (IRIS + smolagents)")
        gr.Markdown("Ask about your orders, shipping, returns, or warranty.")
        
        with gr.Row():
            with gr.Column(scale=2):
                # Email input - collapsible
                with gr.Accordion("📧 Email Settings", open=False):
                    email_input = gr.Textbox(
                        label="Email", 
                        value="alice@example.com", 
                        placeholder="you@example.com",
                        info="Enter your email to access your orders and personal data"
                    )
                
                # Sample prompts section - collapsible
                with gr.Accordion("💡 Sample Questions", open=False):
                    gr.Markdown("*Click any question to load and send it automatically*")
                    with gr.Row():
                        prompt_buttons = []
                        for i in range(0, len(SAMPLE_PROMPTS), 2):
                            with gr.Column():
                                for j in range(2):
                                    if i + j < len(SAMPLE_PROMPTS):
                                        btn = gr.Button(
                                            SAMPLE_PROMPTS[i + j], 
                                            size="sm",
                                            elem_classes=["prompt-button"]
                                        )
                                        prompt_buttons.append(btn)
                
                chatbot = gr.Chatbot(height=400, label="Chat", type="tuples")
                msg_input = gr.Textbox(
                    placeholder="Type your question or click a sample above… (Shift+Enter to submit)", 
                    label="Message",
                    lines=2
                )
                
                with gr.Row():
                    submit_btn = gr.Button("Send", variant="primary")
                    clear_btn = gr.Button("Clear")
            
            with gr.Column(scale=1):
                gr.Markdown("### 🔍 Agent Debug Information")
                gr.Markdown("*Real-time view of agent reasoning, tool calls, and execution steps*")
                debug_display = gr.HTML(
                    visible=True,
                    elem_classes=["debug-container"]
                )
        
        def user_submit(message, history):
            if not message.strip():
                return "", history, ""
            
            history = history + [[message, None]]
            return "", history, ""
        
        def bot_respond(history, email):
            if not history or history[-1][1] is not None:
                return history, ""
            
            user_message = history[-1][0]
            bot_response, debug_info = respond_with_debug(user_message, email)
            history[-1][1] = bot_response
            
            return history, debug_info
        
        
        def fill_prompt(prompt_text):
            return prompt_text
        
        # Event handlers
        submit_btn.click(
            user_submit,
            inputs=[msg_input, chatbot],
            outputs=[msg_input, chatbot, debug_display]
        ).then(
            bot_respond,
            inputs=[chatbot, email_input],
            outputs=[chatbot, debug_display]
        )
        
        msg_input.submit(
            user_submit,
            inputs=[msg_input, chatbot],
            outputs=[msg_input, chatbot, debug_display]
        ).then(
            bot_respond,
            inputs=[chatbot, email_input],
            outputs=[chatbot, debug_display]
        )
        
        clear_btn.click(lambda: ([], ""), outputs=[chatbot, debug_display])
        
        # Connect prompt buttons to fill message box and send
        for btn in prompt_buttons:
            btn.click(
                fill_prompt,
                inputs=[btn],
                outputs=[msg_input]
            ).then(
                user_submit,
                inputs=[msg_input, chatbot],
                outputs=[msg_input, chatbot, debug_display]
            ).then(
                bot_respond,
                inputs=[chatbot, email_input],
                outputs=[chatbot, debug_display]
            )
    
    demo.launch(server_name="0.0.0.0", server_port=int(os.getenv("PORT", "7860")), share=False)

if __name__ == "__main__":
    main()
