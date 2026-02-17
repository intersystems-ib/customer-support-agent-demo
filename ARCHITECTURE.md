# ARCHITECTURE.md

This file provides guidance when working with code in this repository.

## Project Overview

This is a Customer Support Agent demo built with Python and InterSystems IRIS. The agent uses AI (smolagents framework) to help users resolve questions about orders, products, shipping, and warranty using multiple data sources:

- **Structured data**: SQL queries on customers, orders, products, shipments
- **Unstructured data**: RAG (Retrieval Augmented Generation) queries on documentation
- **Live integrations**: IRIS interoperability for shipping status

## Architecture

The project follows a modular architecture:

- **agent/**: AI agent implementation using smolagents CodeAgent
  - `customer_support_agent.py`: Main agent class that orchestrates tools
  - `tools/`: Individual tools for SQL, RAG, and shipping operations
- **db/**: Database client for InterSystems IRIS connection
- **cli/**: Command-line interface for running the agent
- **ui/**: Gradio web interface
- **scripts/**: Utility scripts for embedding documents
- **iris/**: InterSystems IRIS container configuration and data

## Common Commands

### Environment Setup
```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Mac/Linux
# .venv\Scripts\Activate.ps1  # Windows PowerShell

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env to add OPENAI_API_KEY
```

### Database Setup
```bash
# Start IRIS container
docker compose build
docker compose up -d

# Load SQL data (run in IRIS SQL Explorer at http://localhost:52773)
LOAD SQL FROM FILE '/app/iris/sql/schema.sql' DIALECT 'IRIS' DELIMITER ';'
LOAD SQL FROM FILE '/app/iris/sql/load_data.sql' DIALECT 'IRIS' DELIMITER ';'

# Embed documents for RAG
python scripts/embed_sql.py
```

### Running the Agent
```bash
# One-shot mode
python -m cli.run --email alice@example.com --message "Where is my order #1001?"

# Interactive CLI
python -m cli.run --email alice@example.com

# Web UI
python -m ui.gradio
# Then open http://localhost:7860
```

### Local Development with Ollama
```bash
# Download models
ollama pull nomic-embed-text:latest
ollama pull devstral:24b-small-2505-q4_K_M

# Update .env for local models
OPENAI_MODEL=devstral:24b-small-2505-q4_K_M
OPENAI_API_BASE=http://localhost:11434/v1
EMBEDDING_CONFIG_NAME=ollama-nomic-config
```

## Key Components

### Agent Tools
The agent uses three types of tools located in `agent/tools/`:

1. **SQL Tools** (`sql_tool.py`): Query structured data
   - `SQLLastOrdersTool`: Get recent orders for a user
   - `SQLOrderByIdTool`: Get specific order details
   - `SQLOrdersInRangeTool`: Get orders in date range

2. **RAG Tools** (`rag_tool.py`): Query unstructured documents
   - `RAGDocSearchTool`: Search documentation (FAQs, policies)
   - `RAGProductSearchTool`: Search product information

3. **Shipping Tool** (`shipping_tool.py`): Live shipping status via IRIS interoperability

### Database Integration
- Uses InterSystems IRIS with vector search capabilities
- Connection managed through `db/iris_client.py`
- Supports both SQL queries and vector similarity search
- Default connection: localhost:1972, namespace USER, credentials SuperUser/SYS

### Security
- Email-based access control: Users can only access their own order data
- Customer ID verification in all SQL tools
- Environment-based configuration for sensitive data

## Development Notes

- The agent uses smolagents' CodeAgent which generates Python code step-by-step
- Tools are auto-documented through docstrings for the agent's understanding
- Maximum 8 steps per agent run (configurable via AGENT_MAX_STEPS)
- Supports both OpenAI and local Ollama models
- Vector embeddings use text-embedding-3-small (OpenAI) or nomic-embed-text (Ollama)

## Database Schema

Key tables in Agent_Data namespace:
- `Customers`: Customer information with email lookup
- `Orders`: Order data linked to customers and products
- `Products`: Product catalog with embeddings for semantic search
- `Shipments`: Shipping information linked to orders
- `DocChunks`: Document chunks with embeddings for RAG queries

## Testing

No formal test framework is configured. Test the agent manually using:
- CLI commands with different user emails and queries
- Web UI at http://localhost:7860
- Direct IRIS queries in Management Portal at http://localhost:52773

## Environment Variables

Required:
- `OPENAI_API_KEY`: OpenAI API key (or omit for Ollama)

Optional:
- `OPENAI_MODEL`: Model name (default: gpt-4o-mini)
- `OPENAI_API_BASE`: API base URL (default: OpenAI, set to http://localhost:11434/v1 for Ollama)
- `OPENAI_TEMPERATURE`: Model temperature (default: 0.2)
- `AGENT_MAX_STEPS`: Max agent steps (default: 8)
- `AGENT_VERBOSITY`: Verbosity level 0-2 (default: 1)
- `EMBEDDING_CONFIG_NAME`: IRIS embedding config (default: my-openai-config)
- `IRIS_*`: Database connection settings (defaults work with docker-compose)