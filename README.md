# Kenya Investment Explorer

Explore investment opportunities in Kenya — company stake (share) prices and returns per
financial year — with a [Groq](https://groq.com) AI assistant you can ask natural-language
questions about the data.

> ⚠️ **Sample data disclaimer**: The dataset (NSE-listed Kenyan companies, stake prices, and
> per-financial-year returns) is illustrative/placeholder data for demonstration purposes. It is
> **not** live market data and nothing in this app is financial advice. Swap in a real data
> source before using it to make investment decisions.

## Architecture (branch: `frontend-propasal`)

This branch splits the app into two surfaces that share one dataset:

- **`app.py` (Streamlit)** — the chatbox only. Renders the Groq AI chat panel.
- **`frontend/` (Next.js)** — the data browsing UI: filters, table, and bar chart. It embeds the
  Streamlit chat via an `<iframe>` so chatting still happens in Streamlit, but everything is
  presented as one page.
- **`data/companies.json`** — single source of truth for the dataset, read by both `app.py` and
  the Next.js server component (`frontend/src/lib/data.ts`).

```
data/companies.json   Shared dataset (both apps read this)
app.py                Streamlit app — Groq AI chatbox only
frontend/              Next.js app — filters, table, chart, embeds the Streamlit chat
.streamlit/config.toml Streamlit server config (CORS/XSRF relaxed for iframe embedding)
requirements.txt      Python dependencies
.env.example           Template for Streamlit env vars (copy to .env)
```

## Setup

### Streamlit (chat)

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and add your Groq API key (get one at
   [console.groq.com](https://console.groq.com/keys)):

   ```
   GROQ_API_KEY=your-key-here
   GROQ_MODEL=openai/gpt-oss-120b
   ```

### Next.js (dashboard)

```bash
cd frontend
npm install
cp .env.local.example .env.local
```

`NEXT_PUBLIC_STREAMLIT_URL` in `.env.local` should point at wherever the Streamlit app is
running (defaults to `http://localhost:8503`).

## Run locally

In one terminal, start the Streamlit chat on port 8503:

```bash
streamlit run app.py --server.port 8503
```

In another terminal, start the Next.js dashboard:

```bash
cd frontend
npm run dev
```

Open http://localhost:3000 — the dashboard loads the data table/filters/chart, with the Groq AI
chat embedded at the bottom (served by Streamlit on port 8503).

## Deploying

- **Next.js → Vercel**: point a Vercel project at this repo with root directory `frontend/`, and
  set `NEXT_PUBLIC_STREAMLIT_URL` to the public URL of the deployed Streamlit app (Vercel can't
  host the long-running Streamlit process itself).
- **Streamlit → Streamlit Community Cloud** (or any host that runs a persistent Python process):
  deploy `app.py` from the repo root, with `GROQ_API_KEY` set as a secret. Streamlit Community
  Cloud allows framing via `<iframe>`, matching `.streamlit/config.toml`.
