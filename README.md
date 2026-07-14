# Travel Planner using LangGraph And AI

A real world multi agent AI system built with LangGraph. Five AI agents work together to plan a complete trip automatically, from flights and hotels to restaurant recommendations and a day by day itinerary, with conversation memory persisted in PostgreSQL.

## Features

- ✈️ Flight Search Agent
- 🏨 Hotel Search Agent
- 🍜 Food Agent (restaurant recommendations)
- 🗓️ Itinerary Planning Agent
- 🤖 Final Response Agent
- 🧠 Long term memory using PostgreSQL checkpointing
- 🌐 Real time API integration
- 💻 Streamlit web interface

---

## Tech Stack

- LangGraph
- LangChain
- Groq (Llama 3.3 70B)
- PostgreSQL
- Streamlit
- Tavily API (hotel and web search)
- AviationStack API (flight data)
- Google Places API (restaurant search)

---

## How It Works

The system runs a linear graph of five agents. Each agent updates a shared state object, and every step is checkpointed to PostgreSQL so a session can be resumed later using its thread ID.

1. **Flight Agent** searches flights via AviationStack
2. **Hotel Agent** searches hotels via Tavily
3. **Food Agent** searches restaurants via Google Places
4. **Itinerary Agent** builds a travel plan from the flight, hotel, and restaurant results
5. **Final Agent** combines everything into a single polished response
6. **PostgreSQL** stores the conversation state as memory

---

## Setup

### Step 1: Create a Python environment

Open a terminal inside the project folder and run:

```bash
python -m venv langgraph_env3
```

Activate it.

**Windows**

```bash
langgraph_env3\Scripts\activate
```

**macOS / Linux**

```bash
source langgraph_env3/bin/activate
```

---

### Step 2: Install dependencies

```bash
pip install langgraph langchain langchain-openai langchain-groq langchain-community langchain-tavily python-dotenv tavily-python requests streamlit
```

```bash
pip install -U "psycopg[binary,pool]" langgraph-checkpoint-postgres
```

The second line is important. `PostgresSaver` does not ship with the base `langgraph` package. It lives in `langgraph-checkpoint-postgres`, so skipping that line causes an unresolved import for `langgraph.checkpoint.postgres`.

---

### Step 3: Install PostgreSQL

Download and install from https://www.postgresql.org/download/

While installing, note down two things, because you will need them for the connection string:

- The PostgreSQL password you set
- The port number (default is 5432)

---

### Step 4: Create the database

Open pgAdmin or psql and run:

```sql
CREATE DATABASE langgraph_memory_demo;
```

---

### Step 5: Set up the Google Places API

The Food Agent uses the Google Places API. This needs three things to all live on the same Google Cloud project: the API enabled, billing attached, and an API key. If any of these are on a different project, calls fail with `REQUEST_DENIED`.

1. Go to https://console.cloud.google.com
2. Create a dedicated project (project dropdown at the top, then "New project"). Name it something like `travel-planner`.
3. Select that project in the top dropdown so it is the active project.
4. In the top search bar, type "Places API", open it, and click "Enable". Use the legacy "Places API" (service `places-backend.googleapis.com`), not "Places API (New)", since the tool uses the Text Search endpoint.
5. Open the left menu, go to "Billing", and link a billing account. Google requires this even for the free tier. You will not be charged under light testing usage.
6. Go to "APIs and Services", then "Credentials", click "Create credentials", then "API key". Creating the key while your project is selected guarantees it belongs to the right project.

Avoid the "Maps Platform Demo Project" that appears in the project list. It is a Google sandbox and is not meant for your own keys.

---

### Step 6: Create the `.env` file

Create a `.env` file in the project root with the following keys:

```
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
AVIATIONSTACK_API_KEY=your_aviationstack_api_key
GOOGLE_API_KEY=your_google_places_api_key
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/langgraph_memory
```

Match the password and port in `DATABASE_URL` to what you set during PostgreSQL installation. If your Postgres runs on 5433, change the port in the URL to 5433.

---

### Step 7: Get your API keys

| Service | URL |
| --- | --- |
| Groq | https://console.groq.com |
| Tavily | https://tavily.com |
| AviationStack | https://aviationstack.com |
| Google Places | https://console.cloud.google.com |

---

## Running the Application

### Terminal (test the multi agent pipeline)

```bash
python main.py
```

You will be prompted to enter a travel request. This is the fastest way to confirm the full agent graph works before launching the UI.

### Streamlit web app

```bash
streamlit run frontend.py
```

This opens the web interface at http://localhost:8501

### Example prompt

```
Give me a travel plan from Delhi to Glasgow under 4 lakhs for a couple.
```

---

## Troubleshooting

**`Unresolved reference 'PostgresSaver'` or `cannot find reference 'postgres'`**

The `langgraph-checkpoint-postgres` package is missing from the environment your editor or terminal is using. Install it with the Step 2 command. If the terminal import works but your IDE still shows red squiggles, point the IDE interpreter at `langgraph_env3` rather than a global Python.

**`psycopg.errors.ActiveSqlTransaction: CREATE INDEX CONCURRENTLY cannot run inside a transaction block`**

The checkpointer setup runs migrations that cannot execute inside a transaction. The database connection must use autocommit. In `main.py`, the connection should be:

```python
_conn = psycopg.connect(DATABASE_URL, autocommit=True)
```

If a previous failed run left the checkpoint tables half created, drop them and let setup rebuild cleanly:

```bash
psql -U postgres -d langgraph_memory -c "DROP TABLE IF EXISTS checkpoints, checkpoint_blobs, checkpoint_writes, checkpoint_migrations CASCADE;"
```

**Food Agent returns no restaurants, or the final plan has no food section**

Test the tool on its own:

```bash
python -c "from tools.food_tool import search_restaurants; print(search_restaurants('Glasgow'))"
```

If it prints `REQUEST_DENIED`, the API, billing, and key are not all on the same Google Cloud project, or the key has a restriction blocking Places. Recheck Step 5. If it returns real restaurants but they still do not show in the final plan, confirm the itinerary and final prompts in `main.py` include `food_results`.

**Connection refused when starting the app**

PostgreSQL is not running, or the port in `DATABASE_URL` does not match your actual Postgres port. Confirm the service is up and the port is correct.

---

## Project Structure

```
.
├── main.py              # Graph definition, agents, checkpointer, CLI entry point
├── frontend.py          # Streamlit web interface
├── tools/
│   ├── tavily_tool.py   # Hotel and web search via Tavily
│   ├── flight_tool.py   # Flight search via AviationStack
│   └── food_tool.py     # Restaurant search via Google Places
├── .env                 # API keys and database URL (not committed)
└── README.md
```
