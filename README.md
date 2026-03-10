# AI Crew for Trip Planning

## Introduction

This project demonstrates how to use the **CrewAI framework (latest stable release)** to automate trip planning when you're deciding between multiple destinations.

CrewAI orchestrates autonomous AI agents that collaborate to:

- Research destinations  
- Compare options  
- Gather relevant information  
- Build a complete travel itinerary based on your preferences  

Originally inspired by work from [@joaomdmoura](https://x.com/joaomdmoura), **this version has been refactored to align with the latest CrewAI APIs, removing deprecated tools and resolving dependency conflicts.**

---

## Table of Contents

- [CrewAI Framework](#crewai-framework)  
- [Installation](#installation)  
- [Environment Configuration](#environment-configuration)  
- [Running the Script](#running-the-script)  
- [Project Structure](#project-structure)  
- [Using Different LLM Providers](#using-different-llm-providers)  
  - [Using OpenAI (Recommended)](#using-openai-recommended)  
  - [Using GPT-3.5 Instead of GPT-4](#using-gpt-35-instead-of-gpt-4)  
  - [Using Local Models with Ollama](#using-local-models-with-ollama)  
- [What Was Updated](#what-was-updated)  
- [License](#license)

---

## CrewAI Framework

CrewAI enables structured collaboration between role-based AI agents.

In this project:

- A **City Researcher** gathers destination insights  
- A **Local Expert** provides cultural and local knowledge  
- A **Travel Planner** builds a complete itinerary  

All agents collaborate within a Crew to produce a final trip plan.

This implementation uses the **latest stable CrewAI release**, avoiding deprecated APIs and legacy LangChain integrations.

---

## Installation

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd <repo-name>
```

### 2. Create a Virtual Environment (Recommended)

```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows
```

### 3. Install Dependencies

If using Poetry:

```bash
poetry install
```

Or with pip:

```bash
pip install -r requirements.txt
```

---

## Environment Configuration

Create a `.env` file in the root directory:

```env
OPENAI_API_KEY=your_openai_key_here
SERPER_API_KEY=your_serper_key_here
BROWSERLESS_API_KEY=your_browserless_key_here
```

> ⚠️ If using OpenAI models (GPT-4, GPT-3.5), usage will incur API costs.

---

## Running the Script

Run:

```bash
python main.py
```

You will be prompted to enter your trip idea (for example:  
“Beach vacation in Europe” or “Adventure trip in South America”).

The CrewAI agents will collaborate and generate a complete itinerary.

---

## Project Structure

```
.
├── main.py
├── web_app.py
├── trip_agents.py
├── trip_tasks.py
├── tools/
│   ├── search_tools.py
│   └── browser_tools.py
└── README.md
```

### Key Files

- `main.py` – Entry point that builds and runs the Crew  
- `web_app.py` – FastAPI web UI that exposes a browser-based interface  
- `trip_agents.py` – Agent definitions  
- `trip_tasks.py` – Task prompts and descriptions  
- `tools/` – Custom tools used by agents  

All files have been updated to remove deprecated patterns and align with the latest CrewAI APIs.

---

# Using Different LLM Providers

---

## Using OpenAI (Recommended)

Example configuration using the latest LangChain OpenAI integration:

```python
from crewai import Agent
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.7
)

local_expert = Agent(
    role="Local Expert",
    goal="Provide the best insights about the selected city",
    backstory="A knowledgeable local guide with deep cultural understanding.",
    tools=[...],
    llm=llm,
    verbose=True
)
```

---

## Using GPT-3.5 Instead of GPT-4

To switch models, simply change the model parameter:

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.7
)
```

Then pass `llm=llm` into your desired agents.

No other code changes are required.

---

## Using Local Models with Ollama

CrewAI supports local LLMs such as Ollama.

### 1. Install Ollama

Follow the official installation guide from Ollama.

Start a model:

```bash
ollama run llama3
```

---

### 2. Configure Ollama in Code

```python
from langchain_community.llms import Ollama
from crewai import Agent

ollama_llm = Ollama(
    model="llama3",
    base_url="http://localhost:11434"
)

local_expert = Agent(
    role="Local Expert",
    goal="Provide detailed local insights",
    backstory="An experienced travel local.",
    tools=[...],
    llm=ollama_llm,
    verbose=True
)
```

---

### Recommended Modelfile Tweaks

When customizing a local model:

- Add `Observation` as a stop word  
- Tune `temperature`  
- Tune `top_p`  

This improves multi-agent reasoning consistency.

---

## What Was Updated

- Removed deprecated `langchain.chat_models`  
- Updated imports to `langchain_openai` and `langchain_community`  
- Aligned code with latest CrewAI stable API  
- Added optional FastAPI-based web UI for showcasing trip plans  
- Resolved dependency conflicts  
- Simplified setup instructions  
- Updated LLM configuration examples  

---

## License

This project is released under the MIT License.

---

## Web UI (Browser-Based Trip Planning)

In addition to the CLI, you can run a small web app to collect trip details from a browser and display the generated itinerary.

### 1. Install dependencies

Ensure your environment is activated, then install dependencies (FastAPI, Uvicorn, etc. are already listed in `pyproject.toml`):

```bash
poetry install
# or, if using pip
pip install -e .

poetry run uvicorn web_app:app --reload
```
Open http://127.0.0.1:8000/

Make sure your `.env` file is present at the project root so the web server can load:

```env
OPENAI_API_KEY=your_openai_key_here
SERPER_API_KEY=your_serper_key_here
BROWSERLESS_API_KEY=your_browserless_key_here
```

### 2. Run the web server

From the project root:

```bash
uvicorn web_app:app --reload
```

Then open `http://127.0.0.1:8000/` in your browser.

### 3. What the web UI does

- Renders a simple form where you can enter:
  - Origin city
  - Candidate cities (comma-separated)
  - Trip dates or date range
  - Interests and travel style
- On submit, the app calls the same CrewAI-based planner used by `main.py` and displays the resulting itinerary in a styled result page.

