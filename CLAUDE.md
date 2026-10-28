# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

豫树扫地机器人智能客服 — a Streamlit-based intelligent customer service chatbot for robot vacuum cleaners, built with LangChain/LangGraph ReAct Agent + RAG (ChromaDB vector store) + Alibaba Tongyi LLM.

## Commands

```bash
# Run the Streamlit app
streamlit run app.py

# Load documents into the vector store
python -m rag.vector_store

# Test RAG summarization standalone
python -m rag.rag_service

# Test the ReAct agent standalone (no UI)
python -m agent.react_agent
```

## Architecture

### Tech Stack
- **UI**: Streamlit with custom CSS
- **LLM**: Alibaba Tongyi `qwen-turbo` via `langchain_community.chat_models.tongyi.ChatTongyi`
- **Embeddings**: Alibaba DashScope `text-embedding-v3`
- **Vector Store**: ChromaDB (local persistent, `chroma_db/`)
- **Agent**: LangGraph `create_agent` with ReAct pattern
- **Config**: YAML files in `config/`

### Core Data Flow
```
User Query → ReactAgent.execute_stream()
  → LangGraph ReAct loop (think → act → observe → repeat)
    → Tools: rag_summarize, get_weather, get_user_id, etc.
    → Middleware: monitor/ caching, logging, dynamic prompt switching
  → Streaming response chunks → Streamlit UI
```

### Key Components

**`agent/react_agent.py`** — ReAct Agent wrapper. Creates a LangGraph agent with system prompt, tools, and middleware. `execute_stream()` streams responses via `agent.stream()` with `stream_mode="values"`.

**`agent/tools/middleware.py`** — Three middleware hooks:
- `monitor_tool` (@wrap_tool_call): MD5-based tool call caching via `runtime.tool_cache`, timing/stats tracking, and sets `runtime.context["report"] = True` when `fill_context_for_report` is called
- `log_before_model` (@before_model): Logs message count and latest message before each model call
- `report_prompt_switch` (@dynamic_prompt): Switches system prompt to `report_prompt.txt` when `runtime.context.report` is True, otherwise uses `main_prompt.txt`

**`agent/tools/agent_tools.py`** — 7 LangChain tools. `fill_context_for_report` is the trigger that flips the middleware context to report mode. Report flow: `get_user_id` → `get_current_month` → `fill_context_for_report` → `fetch_external_data`.

**`rag/rag_service.py`** — RAG pipeline: query rewrite (via LLM) → ChromaDB retrieval → LLM summarization with `rag_summarize.txt` prompt. Uses LCEL chain (`prompt | model | StrOutputParser`).

**`rag/vector_store.py`** — ChromaDB wrapper with MD5-based document deduplication. Loads txt/pdf from `data/`, splits via `RecursiveCharacterTextSplitter`, stores in `chroma_db/`. Tracks processed files in `md5.text`.

**`model/factory.py`** — Factory pattern for `ChatTongyi` and `DashScopeEmbeddings`. Module-level singletons `chat_model` and `embed_model` are imported throughout the codebase.

**`utils/`**:
- `path_tool.py` — `get_abs_path()` resolves relative paths from project root (derived from `utils/` directory location)
- `config_handler.py` — Loads 4 YAML configs as module-level dicts: `rag_conf`, `chroma_conf`, `prompts_conf`, `agent_conf`
- `prompt_loader.py` — Loads three prompt templates from text files

### Dynamic Prompt Switching

The middleware detects report-generation intent via tool calls. When the agent calls `fill_context_for_report`, `monitor_tool` sets `runtime.context.report = True`. On the next model call, `report_prompt_switch` (registered as `@dynamic_prompt`) reads this flag and swaps the system prompt from `main_prompt.txt` to `report_prompt.txt`.

### Config Files
- `config/rag.yml` — LLM model name, embedding model name, retrieval/cache/timeout settings
- `config/chroma.yml` — Vector store collection name, chunking params, data path, allowed file types
- `config/prompts.yml` — Paths to three prompt template files
- `config/agent.yml` — Path to external CSV data
