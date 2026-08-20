# Kenya Investment Explorer

A Streamlit app for exploring investment opportunities in Kenya — company stake (share) prices
and returns per financial year — with a [Groq](https://groq.com) AI assistant you can ask
natural-language questions about the data.

> ⚠️ **Sample data disclaimer**: The dataset bundled with this app (NSE-listed Kenyan companies,
> stake prices, and per-financial-year returns) is illustrative/placeholder data for
> demonstration purposes. It is **not** live market data and nothing in this app is financial
> advice. Swap in a real data source before using it to make investment decisions.

## Features

- Table of sample NSE-listed Kenyan companies with sector, stake price (KES/share), market cap,
  and returns for FY2021–FY2025.
- Sidebar filters: sector, max stake price, minimum average return.
- Bar chart of average return by company for the filtered set.
- Groq-AI-powered chat assistant that answers questions about the (filtered) dataset.

## Setup

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and add your Groq API key (get one at
   [console.groq.com](https://console.groq.com/keys)):

   ```bash
   cp .env.example .env
   ```

   ```
   GROQ_API_KEY=your-key-here
   GROQ_MODEL=openai/gpt-oss-120b
   ```

   The app runs fine without a key — the data table/filters/chart all work; only the AI chat
   panel requires it.

## Run

```bash
streamlit run app.py
```

Then open the URL Streamlit prints (typically http://localhost:8501).

## Project structure

```
app.py            Streamlit app (data, filters, chart, Groq chat)
requirements.txt  Python dependencies
.env.example      Template for local environment variables (copy to .env)
.gitignore        Excludes .env and local/build artifacts from git
```
