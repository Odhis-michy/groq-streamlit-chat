"""Kenya Investment Explorer — browse sample NSE stake prices & returns, ask Groq AI about them."""

import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

RETURN_YEARS = ["FY2021", "FY2022", "FY2023", "FY2024", "FY2025"]

SAMPLE_DATA = [
    # Company, Sector, Stake Price (KES/share), Market Cap (KES Bn), FY2021..FY2025 return %
    ("Safaricom PLC", "Telecommunications", 17.50, 700.0, 12.4, -8.1, 5.6, 18.9, 22.3),
    ("Equity Group Holdings", "Banking", 45.20, 171.0, 22.1, 9.8, -3.4, 14.7, 19.5),
    ("KCB Group", "Banking", 38.75, 124.0, 15.6, -5.2, 8.9, 21.3, 17.8),
    ("East African Breweries (EABL)", "Consumer Goods", 165.00, 130.0, 8.3, 4.1, -6.7, 11.2, 9.4),
    ("British American Tobacco Kenya", "Consumer Goods", 340.00, 34.0, 6.5, 2.3, 7.8, -4.5, 10.1),
    ("Co-operative Bank of Kenya", "Banking", 13.85, 81.0, 18.9, 6.4, 1.2, 16.5, 13.7),
    ("Absa Bank Kenya", "Banking", 15.60, 95.0, 20.3, 11.7, -2.1, 13.4, 16.2),
    ("Bamburi Cement (Portland)", "Manufacturing", 55.00, 21.0, -4.2, -12.5, 9.6, 24.8, 15.3),
    ("Kenya Airways (KQ)", "Aviation", 3.85, 22.0, -25.4, -18.6, -9.3, 12.1, 8.7),
    ("Britam Holdings", "Insurance", 6.40, 24.0, 9.7, 3.5, -1.8, 15.9, 12.6),
    ("Jubilee Holdings", "Insurance", 210.00, 18.0, 7.2, 5.9, 4.3, 10.6, 11.8),
    ("Stanbic Holdings", "Banking", 132.00, 51.0, 16.4, 8.2, 2.7, 18.3, 14.9),
    ("KenGen", "Energy", 3.10, 52.0, 5.8, -3.9, 11.4, 20.7, 16.5),
    ("Nation Media Group", "Media", 20.50, 3.5, -6.1, -10.2, 2.4, 7.8, 6.3),
]

COLUMNS = ["Company", "Sector", "Stake Price (KES/share)", "Market Cap (KES Bn)", *RETURN_YEARS]


@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.DataFrame(SAMPLE_DATA, columns=COLUMNS)
    df["Avg Return %"] = df[RETURN_YEARS].mean(axis=1).round(2)
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
        max_tokens=600,
    )
    return completion.choices[0].message.content


def main() -> None:
    st.set_page_config(page_title="Kenya Investment Explorer", page_icon="📈", layout="wide")
    st.title("📈 Kenya Investment Explorer")
    st.caption("Browse sample stake prices and returns for NSE-listed Kenyan companies, and ask Groq AI about them.")
    st.warning(
        "⚠️ **Sample/illustrative data only** — figures below are placeholder demo data, "
        "not live market data, and nothing on this page is financial advice.",
        icon="⚠️",
    )

    df = load_data()

    st.sidebar.header("Filters")
    sectors = sorted(df["Sector"].unique())
    selected_sectors = st.sidebar.multiselect("Sector", sectors, default=sectors)

    max_price = float(df["Stake Price (KES/share)"].max())
    price_cap = st.sidebar.slider(
        "Max stake price (KES/share)", 0.0, max_price, max_price, step=1.0
    )

    min_avg_return = st.sidebar.slider(
        "Min average return (%)", -30.0, 30.0, -30.0, step=0.5
    )

    filtered = df[
        df["Sector"].isin(selected_sectors)
        & (df["Stake Price (KES/share)"] <= price_cap)
        & (df["Avg Return %"] >= min_avg_return)
    ]

    st.subheader(f"Investment opportunities ({len(filtered)} companies)")
    st.dataframe(filtered.set_index("Company"), use_container_width=True)

    if not filtered.empty:
        st.subheader("Average return by company")
        st.bar_chart(filtered.set_index("Company")["Avg Return %"])

    st.divider()
    st.subheader("🤖 Ask Groq AI about these opportunities")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if not GROQ_API_KEY:
        st.info(
            "Set `GROQ_API_KEY` in a `.env` file (see `.env.example`) to enable the AI assistant. "
            "The rest of the app works without it.",
            icon="🔑",
        )
    else:
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
                        build_ai_context(filtered if not filtered.empty else df),
                        st.session_state.chat_history[:-1],
                    )
                except Exception as exc:  # noqa: BLE001 - surface any API/config error to the user
                    answer = f"Sorry, the AI assistant hit an error: `{exc}`"
                st.markdown(answer)

            st.session_state.chat_history.append({"role": "assistant", "content": answer})


if __name__ == "__main__":
    main()
