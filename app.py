"""Kenya Investment Explorer — Groq AI chatbox.

Data browsing/filtering/charts live in the Next.js frontend (see `frontend/`); this
Streamlit app is embedded there (via iframe) and only handles the chat panel.
"""

import json
import os
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b")

DATA_PATH = Path(__file__).parent / "data" / "companies.json"


@st.cache_data
def load_data() -> pd.DataFrame:
    raw = json.loads(DATA_PATH.read_text())
    rows = []
    for c in raw["companies"]:
        row = {
            "Company": c["company"],
            "Sector": c["sector"],
            "Stake Price (KES/share)": c["stakePrice"],
            "Market Cap (KES Bn)": c["marketCap"],
            **c["returns"],
        }
        rows.append(row)
    df = pd.DataFrame(rows)
    df["Avg Return %"] = df[raw["returnYears"]].mean(axis=1).round(2)
    return df


def build_ai_context(df: pd.DataFrame) -> str:
    return df.to_csv(index=False)


def ask_groq(question: str, context_csv: str, history: list[dict]) -> str:
    from groq import Groq

    client = Groq(api_key=GROQ_API_KEY)
    system_prompt = (
        "You are an investment research assistant focused on the Kenyan market (NSE). "
        "Answer questions using ONLY the sample dataset (CSV) provided below as context. "
        "The data is illustrative/sample data for a demo app, not live market data — "
        "if the user seems to want financial advice, remind them this is not financial advice "
        "and figures are illustrative.\n\nDataset (CSV):\n" + context_csv
    )
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": question})

    completion = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        temperature=0.3,
        max_tokens=800,
    )
    return completion.choices[0].message.content


def hide_chrome_for_iframe() -> None:
    """Trim Streamlit's own header/footer/padding so this reads cleanly inside an <iframe>."""
    st.markdown(
        """
        <style>
        #MainMenu, header, footer {visibility: hidden;}
        .block-container {padding-top: 1rem; padding-bottom: 1rem;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(page_title="Kenya Investment Explorer — Chat", page_icon="🤖", layout="centered")
    hide_chrome_for_iframe()

    st.subheader("🤖 Ask Groq AI about Kenyan NSE investment opportunities")

    df = load_data()

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if not GROQ_API_KEY:
        st.info(
            "Set `GROQ_API_KEY` in a `.env` file (see `.env.example`) to enable the AI assistant.",
            icon="🔑",
        )
        return

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    question = st.chat_input("e.g. Which sectors had the best average returns?")
    if question:
        st.session_state.chat_history.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            try:
                answer = ask_groq(
                    question,
                    build_ai_context(df),
                    st.session_state.chat_history[:-1],
                )
            except Exception as exc:  # noqa: BLE001 - surface any API/config error to the user
                answer = f"Sorry, the AI assistant hit an error: `{exc}`"
            st.markdown(answer)

        st.session_state.chat_history.append({"role": "assistant", "content": answer})


if __name__ == "__main__":
    main()
