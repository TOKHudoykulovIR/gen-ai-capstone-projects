import streamlit as st
import pandas as pd
import numpy as np
from app import GITHUB_REPO, GITHUB_TOKEN, api_key, run_agent
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime

import requests
import sqlite3
import json
import re
import os

st.set_page_config(page_title="DATA INSIGHTS AGENT", layout="wide")

# Initialize session state for chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "logs" not in st.session_state:
    st.session_state.logs = []

# load some info from DB (local, without going to LLM)
def get_database_stats():
    st.session_state.logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Fetched database stats successfully.")

    try:
        conn = sqlite3.connect('movie.sqlite')
        cur = conn.cursor()

        # total films
        cur.execute("SELECT COUNT(*) FROM IMDB;")
        agg = {"total_rows": cur.fetchone()[0]}

        # avg rating
        cur.execute("SELECT AVG(Rating) FROM IMDB WHERE Rating IS NOT NULL;")
        agg["avg_rating"] = cur.fetchone()[0]

        # distinct genres
        cur.execute("SELECT COUNT(DISTINCT genre) FROM genre;")
        agg["distinct_genres"] = cur.fetchone()[0]

        # top 3 genres
        cur.execute(
            "SELECT genre, COUNT(*) AS cnt FROM genre WHERE genre IS NOT NULL AND genre != '' GROUP BY genre ORDER BY cnt DESC LIMIT 3;")
        agg["top_genres"] = cur.fetchall()
        return agg
    except Exception as e:
        return {"error": str(e)}
    finally:
        try:
            conn.close()
        except Exception as ex:
            pass


st.title("🎬 Movie Data Insights App")
st.markdown("Ask questions about movie ratings, revenues, and genres!")

# Sidebar with business information
with st.sidebar:
    st.header("📊 Database Overview")

    stats = get_database_stats()
    if 'error' not in stats:
        total_rows = stats.get("total_rows")
        st.write("Total movies: ", total_rows if total_rows is not None else "Unknown")
        st.write("Average rating: ", round(stats.get("avg_rating") or 0, 2))
        st.write("Distinct genres: ", stats.get("distinct_genres") or "Unknown")
        st.write("Top genres: ")
        topg = stats.get("top_genres") or []
        if topg:
            st.table(pd.DataFrame(topg, columns=["Genre", "Count"]))
        else:
            st.write("No genre stats available.")
    else:
        st.error("Could not load database stats")

    # Clear History button
    if st.button("🗑️ Clear Chat History", type="secondary"):
        st.session_state.chat_history = []
        st.rerun()

    # Sample queries
    st.header("💡 Sample Queries")
    sample_queries = [
        "What are the most common genres?",
        "Which movies have the highest worldwide revenue?",
        "Compare domestic vs worldwide revenue for action movies"
    ]
    for query in sample_queries:
        if st.button(query, key=query):
            st.session_state.user_input = query



st.markdown("---")

# Input form that clears after submission
with st.form("user_input_form", clear_on_submit=True):
    user_input = st.text_input("Ask questions about movie data:")
    submitted = st.form_submit_button("Send")

if submitted and user_input:
    # Convert chat history to the format expected by run_agent
    history_for_agent = []
    for chat in st.session_state.chat_history:
        history_for_agent.append({"role": "user", "content": chat["question"]})
        history_for_agent.append({"role": "assistant", "content": chat["answer"]})

    # Get agent response with history and show loader
    with st.spinner("🤔 Processing your question..."):
        result = run_agent(user_input, history_for_agent)

    # Add to chat history at the beginning (latest first) with timestamp
    st.session_state.chat_history.insert(0, {
        "question": user_input,
        "answer": result,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

# Display chat history with latest at top
if st.session_state.chat_history:
    st.markdown("### Chat History")
    for i, chat in enumerate(st.session_state.chat_history):
        st.markdown(f"**Question:** {chat['question']}")
        st.markdown(f"**Answer:** {chat['answer']}")
        st.markdown(f"**Time: {chat['timestamp']}**")
        if i < len(st.session_state.chat_history) - 1:
            st.markdown("---")

# Logs Console
with st.expander("🧠 Logs Console", expanded=False):
    if st.session_state.logs:
        # Show logs in reverse (latest first)
        for log_entry in reversed(st.session_state.logs):
            st.markdown(f"<small>{log_entry}</small>", unsafe_allow_html=True)
    else:
        st.write("No logs yet.")

    # Optionally: Clear logs button
    if st.button("Clear Logs"):
        st.session_state.logs = []
        st.rerun()
