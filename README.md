# Personal Chatbot Example

A full-stack AI chatbot application with a **FastAPI** backend and a **React** frontend. The backend proxies chat messages to any OpenAI-compatible LLM API (OpenAI, OpenRouter, Ollama, etc.) via LangChain, and the React UI renders responses in real-time using Server-Sent Events (SSE) with full Markdown and LaTeX math support.

---

## What It Does

| Feature | Description |
|---|---|
| **Streaming chat** | Messages are streamed token-by-token from the LLM to the browser via SSE (`text/event-stream`), so responses appear progressively. |
| **Non-streaming mode** | Optionally receive the full response in a single JSON payload by setting `"stream": false` in the request body. |
| **Markdown rendering** | Assistant responses are rendered as rich Markdown — including **GFM tables**, **fenced code blocks**, **lists**, and **links** — powered by `react-markdown` and `remark-gfm`. |
| **LaTeX math** | Mathematical notation (e.g. `$x^2$` or `$$\int_0^1 f(x)\,dx$$`) is rendered with KaTeX via `remark-math` and `rehype-katex`. |
| **Configurable LLM provider** | Swap models and providers by changing environment variables — no code changes required. Works with OpenAI, OpenRouter, Ollama, Azure OpenAI, or any API that implements the OpenAI chat completions interface. |
| **Customisable system prompt** | Define the assistant's personality and behaviour through the `SYSTEM_PROMPT` environment variable. |
| **Static UI serving** | The FastAPI server serves the pre-built React frontend from `ui/dist/`, so a single process handles both API and UI. |

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│  Browser (React SPA)                            │
│  ui/src/App.jsx                                 │
│   • Sends POST /chat with { message, stream }   │
│   • Reads SSE stream and appends tokens         │
│   • Renders Markdown + KaTeX                    │
└──────────────────┬──────────────────────────────┘
                   │ HTTP
┌──────────────────▼──────────────────────────────┐
│  FastAPI Server (main.py)                       │
│   POST /chat                                    │
│   • Streaming: returns text/event-stream         │
│   • Non-streaming: returns JSON { response }     │
│   GET /* → serves ui/dist/ as static files       │
└──────────────────┬──────────────────────────────┘
                   │ HTTPS (OpenAI-compatible API)
┌──────────────────▼──────────────────────────────┐
│  LLM Provider                                   │
│  (OpenAI / OpenRouter / Ollama / etc.)           │
└─────────────────────────────────────────────────┘
```

---

## Project Structure

```
personal-chatbot-example/
├── main.py              # FastAPI application & entry point
├── config.py            # Pydantic Settings (reads .env)
├── pyproject.toml       # Python project metadata & dependencies
├── .python-version      # Pinned Python version (3.13)
├── .env.example         # Template env file (safe to commit)
├── .env                 # Your local env variables (git-ignored)
├── .gitignore
├── uv.lock              # uv lockfile
├── ui/                  # React frontend
│   ├── index.html       # HTML shell
│   ├── package.json     # Node dependencies
│   ├── vite.config.js   # Vite configuration
│   ├── src/
│   │   ├── main.jsx     # React entry point
│   │   ├── App.jsx      # Chat component (SSE + Markdown)
│   │   └── App.css      # Styles
│   └── dist/            # Production build (served by FastAPI)
└── README.md
```

---

## Software Dependencies

### Backend (Python ≥ 3.13)

| Package | Version | Purpose |
|---|---|---|
| `fastapi` | `==0.137.1` | Web framework for the REST/SSE API |
| `uvicorn[standard]` | `>=0.34.0` | ASGI server to run FastAPI |
| `langchain` | `>=1.3.1` | LLM orchestration framework |
| `langchain-openai` | `>=0.2.0` | OpenAI-compatible chat model integration |
| `langchain-core` | `>=0.3.0` | Core abstractions (messages, streaming) |
| `pydantic-settings` | `>=2.0.0` | Typed settings loaded from `.env` files |

### Frontend (Node.js)

| Package | Version | Purpose |
|---|---|---|
| `react` | `^18.3.1` | UI library |
| `react-dom` | `^18.3.1` | React DOM renderer |
| `react-markdown` | `^10.1.0` | Markdown rendering in React |
| `remark-gfm` | `^4.0.1` | GitHub Flavoured Markdown support |
| `remark-math` | `^6.0.0` | Math notation parsing |
| `rehype-katex` | `^7.0.1` | KaTeX rendering for parsed math |
| `vite` | `^6.0.0` | Dev server & build tool |
| `@vitejs/plugin-react` | `^4.3.4` | React support for Vite |

### System-level Requirements

- **Python 3.13+**
- **Node.js** (LTS recommended, e.g. 20.x or 22.x)
- **npm** (ships with Node.js)
- [**uv**](https://docs.astral.sh/uv/) — fast Python package & project manager (recommended; `pip` works too)

---

## Developer Setup

### 1. Clone the repository

```bash
git clone git@github.com:datoin/personal-chatbot-example.git
cd personal-chatbot-example
```

Or via HTTPS:

```bash
git clone https://github.com/datoin/personal-chatbot-example.git
cd personal-chatbot-example
```

### 2. Configure environment variables

Copy the example env file and fill in your values:

```bash
cp .env.example .env
```

Then edit `.env` with your API key and preferred settings:

```env
# Required — your API key for the LLM provider
OPENAI_API_KEY=sk-your-api-key-here

# Optional — override the base URL to use a different provider
# Default: https://api.openai.com/v1
OPENAI_BASE_URL=https://openrouter.ai/api/v1

# Optional — choose the model
# Default: gpt-4o
OPENAI_MODEL=google/gemma-4-31b-it:free

# Optional — customise the assistant's personality
SYSTEM_PROMPT="You are a helpful assistant."
```

> **Note:** `.env` is git-ignored and will never be committed. See `.env.example` for all available options.

> **Tip:** To use a local Ollama instance, set `OPENAI_BASE_URL=http://localhost:11434/v1` and `OPENAI_MODEL` to your local model name (e.g. `llama3`). No API key is needed — set `OPENAI_API_KEY` to any non-empty string.

### 3. Install Python dependencies

Using **uv** (recommended):

```bash
uv sync
```

Or using **pip** with a virtual environment:

```bash
python3.13 -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install -e .
```

### 4. Build the frontend

```bash
cd ui
npm install
npm run build
cd ..
```

This produces the `ui/dist/` directory that FastAPI serves as static files.

### 5. Run the application

Using **uv**:

```bash
uv run python main.py
```

Or with an activated virtual environment:

```bash
python main.py
```

The server starts on **http://localhost:8000** with hot-reload enabled.

- **Chat UI:** [http://localhost:8000](http://localhost:8000)
- **API docs (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## API Reference

### `POST /chat`

Send a message to the chatbot.

**Request body:**

```json
{
  "message": "Hello, how are you?",
  "stream": true
}
```

| Field | Type | Default | Description |
|---|---|---|---|
| `message` | `string` | *(required)* | The user's message |
| `stream` | `boolean` | `true` | If `true`, returns an SSE stream; if `false`, returns a JSON response |

**Streaming response** (`stream: true`):

```
Content-Type: text/event-stream

data: {"token": "Hello"}

data: {"token": "!"}

data: {"token": " How"}

data: [DONE]
```

**Non-streaming response** (`stream: false`):

```json
{
  "response": "Hello! How can I help you today?"
}
```

---

## Frontend Development

For a faster frontend development workflow with hot module replacement:

```bash
cd ui
npm run dev
```

This starts a Vite dev server (typically on `http://localhost:5173`). You'll need to configure a proxy or run the FastAPI backend simultaneously for the `/chat` endpoint to be reachable.

After making changes, rebuild the production bundle:

```bash
npm run build
```

Then restart the FastAPI server to serve the updated files.

---

## Environment Variable Reference

| Variable | Required | Default | Description |
|---|---|---|---|
| `OPENAI_API_KEY` | Yes | `""` | API key for the LLM provider |
| `OPENAI_BASE_URL` | No | `https://api.openai.com/v1` | Base URL of the OpenAI-compatible API |
| `OPENAI_MODEL` | No | `gpt-4o` | Model identifier to use |
| `SYSTEM_PROMPT` | No | `You are a helpful assistant.` | System message that defines the assistant's behaviour |

---

## License

This project is provided as an example. See the repository for any license information.
