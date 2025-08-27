Customer support agent that helps users resolve questions about orders, products, shipping, etc.

You will build an AI agent that:
* Uses a LLM as its "mind" to plan and decide how to answer questions that users will ask about their orders, products, etc. 
* Uses different tools to access structured data (SQL tables), unstructured data (documents using a RAG pattern) and live external information (interoperability).

# Requirements
* Local Python environment to run the agent
* Docker to run an InterSystems IRIS platform container that will enable the agent to access structured and unstructured data and interoperability.
* VSCode to check the code
* An OpenAI API key as we are using OpenAI models as the LLM for the agent and also for embedding documents (RAG)

# Setup

Setup Python Environment
```bash
# create a local venv environment
python3 -m venv .venv
# ... for Windows users
python -m venv .venv

# activate venv
# ... for Mac or Linux users
source .venv/bin/activate
# ... for Windows users
./venv/Scripts/Activate.ps1

# install dependencies
pip3 install -r requirements.txt
```

Create a `.env` file:
* Copy `.env.example` to `.env`
* Modify it to include your OpenAI API

Setup InterSystems IRIS container:
```bash
docker compose build
docker compose up -d
```

You can access IRIS [Management Portal](http://localhost:52773/csp/sys/UtilHome.csp) using:
* User: `superuser`
* Password: `SYS`

# Understanding the repo
Have a look at this summary of the repo contents to understand the project.

```graphql
customer-support-agent/
├─ .env.example             # sample env file (copy to .env)
│
├─ iris/                    # InterSystems IRIS assets
│  ├─ Dockerfile            # IRIS container build
│  ├─ sql/                  # SQL scripts
│  │  ├─ schema.sql         # creates tables for Customer Support use case
│  │  ├─ load_data.sql      # loads CSVs into tables
│  │  └─ truncate.sql      
│  ├─ data/                 # data: customer, orders, etc.
│  │  ├─ customers.csv
│  │  ├─ products.csv
│  │  ├─ orders.csv
│  │  └─ shipments.csv
│  ├─ docs/                 # unstructured Knowledge Base (RAG content)
│  │  ├─ returns_policy.md
│  │  ├─ warranty.md
│  │  ├─ shipping_faq.md
│  │  └─ headphones_guide.md
│  └─ src/                  # IRIS classes. Simulates live shipping status interoperability 
│
├─ agent/                   # the AI agent (Python) + tools
│  ├─ customer_support_agent.py   # wraps smolagents CodeAgent + tools
│  └─ tools/
│     ├─ sql_tool.py              # SQL tools (last_orders/order_by_id/in_range)
│     ├─ rag_tool.py              # RAG tools using IRIS EMBEDDING(...) at query time
│     └─ shipping_tool.py         # calls IRIS interoperability (/api/shipping/status)
│
├─ db/                      # database adapters & helpers
│  └─ iris_client.py        # InterSystems IRIS Python DB-API client (simple connector)
│
├─ cli/                     # terminal frontend to run the agent
│  └─ run.py                
│
├─ ui/                      # lightweight web UI to run the agent
│  └─ gradio.py             
│
└─ scripts/                 # one-off utility scripts
   └─ embed_sql.py          # loads files into Docs & builds vectors via IRIS EMBEDDING() feature
```

# Load SQL Data

Before running the agent, we must create the tables and insert some data.
This will be the structured data that the agent will query to answer user questions.

Run this SQL sentences in IRIS [SQL Explorer](http://localhost:52773/csp/sys/exp/%25CSP.UI.Portal.SQL.Home.zen?$NAMESPACE=USER) or using your favorite SQL client.

```sql
LOAD SQL FROM FILE '/app/iris/sql/schema.sql' DIALECT 'IRIS' DELIMITER ';'
```

```sql
LOAD SQL FROM FILE '/app/iris/sql/load_data.sql' DIALECT 'IRIS' DELIMITER ';' 
```

Check the data you have just inserted and get yourself familiar with the tables.

# Load and embed non structured data
The agent will be able also to query non structured data using a RAG (Retrieval Augmented Generation) pattern.
For that, we will be leveraging InterSystems IRIS Vector Search features.

We will embed the data using OpenAI `text-embedding-3-small` model.
We will leverage an InterSystems IRIS feature that allows us to setup embedding directly in the database.

```sql
INSERT INTO %Embedding.Config (Name, Configuration, EmbeddingClass, VectorLength, Description)
  VALUES ('my-openai-config', 
          '{"apiKey":"your-openai-api-key-here", 
            "sslConfig": "llm_ssl", 
            "modelName": "text-embedding-3-small"}',
          '%Embedding.OpenAI', 
          1536,  
          'a small embedding model provided by OpenAI') 
```

Now, run script that loops over documents and records that needs to be embedded
```bash
python scripts/embed_sql.py
```

After that have a look at the tables and check that embeddings are now included.


# Interoperability
InterSystems IRIS also includes a native interoperability framework to allow your solutions to seamlessly connect to other systems in a robust way.

In this project, we have included a simple mock interoperability service that receives a request and aggregates simulated shipping info and timeline.  
```bash
curl --header "Content-Type: application/json" \
  --request POST \
  --data '{"orderStatus":"Processing","trackingNumber":"DHL7788"}' \
  http://localhost:52773/api/shipping/status
```

This information could also be used by the agent.

Example response:
```json
{
  "info": {
    "trackingCode": "DHL7788",
    "carrier": "DHL",
    "status": "In Transit",
    "eta": "2025-09-02",
    "trace": {
      "sessionId": "2",
      "url": "http://localhost:52773/csp/user/EnsPortal.VisualTrace.zen?SESSIONID=2"
    }
  },
  "timeline": {
    "events": [
      {
        "timestamp": "2025-08-20T00:00:00Z",
        "description": "Package in transit",
        "location": "Rome, IT"
      }
    ]
  }
}
```

# Understanding the agent

The agent is a smolagents CodeAgent:
* It will use an mini OpenAI LLM model as a mind to plan and decide which tools use
* It will run several steps and use different tools to try to resolve a user question

# Running the agent

## One-shot
Try some one-shot commands like this to test your agent.

```bash
python -m cli.run --email alice@example.com --message "Where is my order #1001?"

python -m cli.run --email alice@example.com --message "What is the warranty period of my latest order?"

python -m cli.run --email alice@example.com --message "What is the status of the shipping of my latest order ? Where is it?"
```

## Interactive
```bash
python -m cli.run --email alice@example.com
```
## UI
```bash
python -m ui.gradio
```
