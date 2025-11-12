from datetime import datetime

from dotenv import load_dotenv
from openai import OpenAI

import requests
import sqlite3
import json
import re
import os
import streamlit as st

load_dotenv()  # reads variables from a .env file and sets them in os.environ

api_key = os.getenv("OPENAI_API_KEY")  # get the key from .env
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # personal GitHub account token
GITHUB_REPO = os.getenv("GITHUB_REPO")  # format: "username/repo"

client = OpenAI(api_key=api_key)

instructions_for_sql = """
Table: IMDB
| Column       | Type    | Notes 
| ------------ | ------- |
| Movie_id     | TEXT    | PK
| Title        | TEXT    |
| Rating       | DECIMAL | Rating from 0.0 to 10.0
| TotalVotes   | INTEGER |
| Budget       | DOUBLE  | Budget for the film. May contain NULL or 0 values in database, skip this records
| Runtime      | TEXT    | Runtime in minutes
--------------------------

Table: earning
| Column    | Type    | Notes 
| --------- | ------- | ----- 
| Movie_id  | TEXT    |  
| Domestic  | INTEGER | Domestic Revenue 
| Worldwide | DOUBLE  | Worldwide Revenue 
-------------------------------

Table: genre
| Column   | Type | Notes 
| -------- | ---- | ----- 
| Movie_id | TEXT |       
| genre    | TEXT | choices (Biography, Adventure, Comedy, Drama, Action, Animation, Crime, Mystery, Romance, Thriller, History, Sport, Western, Sci-Fi, Family, Musical, Fantasy, War, Horror, Music)
"""

tools = [
    {
        "type": "function",
        "name": "query_database",
        "description":
            "Execute a SQL SELECT query to retrieve structured data from the connected SQL database. "
            "The agent uses this function whenever the user requests analytical insights, summaries, or information that requires access to the data source."
            "Only relevant table structures or column details may be referenced for query construction"
            "The query must:\n"
            "• Use proper SQL syntax and aliases for joined tables.\n"
            "• Limit the results to 15 rows for performance and privacy.\n"
            "• Retrieve only the fields necessary to answer the user’s question.\n\n",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": f"""
                        A valid SQL SELECT statement that retrieves at most 15 records from the database. 
                        The schema of the table(s) available for querying: {instructions_for_sql}. 
                        Always use table aliases when joining multiple tables to keep column references clear. 
                        Focus on retrieving only the data relevant to the user’s request.
                    """
                }
            },
            "required": ["query"]
        },
    },
    {
        "type": "function",
        "name": "create_github_ticket",
        "description":
            "Use this function ANYTIME the user requests help, or when an error, missing data, or unclear request prevents "
            "the agent from successfully completing the task.\n\n"
            "You MUST call this function if request close to following cases:\n"
            "1. The database query fails, times out, or returns no results when results are expected.\n"
            "2. The user explicitly asks for help, says 'create a ticket', 'contact support', or requests human review.\n"
            "3. The requested data or feature does not exist in the database (e.g., missing table, invalid column).\n"
            "4. The agent detects an unknown error, permission / access requests or cannot interpret the user's question.\n\n"
            "When in doubt — CALL THIS FUNCTION.\n\n"
            "The ticket should summarize the issue clearly and concisely so a human can review it later. "
            "After creating the ticket, print a short confirmation message to the console for logging.",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Title of the support ticket"},
                "description": {"type": "string", "description": "Detailed description of the issue"},
                "labels": {"type": "array", "items": {"type": "string"}, "description": "Labels for the GitHub issue"}
            },
            "required": ["title", "description"]
        }
    }
]

def create_github_ticket(title: str, description: str, labels):
    if not GITHUB_TOKEN or not GITHUB_REPO:
        return {"error": "GitHub token or repo not configured in .env"}

    url = f"https://api.github.com/repos/{GITHUB_REPO}/issues"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    data = {
        "title": title,
        "body": description,
        "labels": labels
    }
    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 201:
        issue_url = response.json().get("html_url")
        return {"success": True, "issue_url": issue_url}
    else:
        return {"success": False, "error": response.json()}

def query_database(query: str):
    print(f"Generated query: {query}")
    if not re.match(r"^\s*SELECT", query, re.I):  # extra layer of check to avoid unsecure queries
        return {"error": "Only SELECT queries allowed! Ask user to create ticket issue in GITHUB"}
    connection = sqlite3.connect("movie.sqlite")  # link to download the db - https://www.kaggle.com/datasets/shahjhanalam/movie-data-analytics-dataset
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        return {"sample_rows": rows}
    except Exception as ex:
        return {"error": str(ex)}
    finally:
        connection.close()  # close connection at the end


def run_agent(user_input, chat_history=None):
    # Start with chat history if provided, otherwise use empty list
    if chat_history is None:
        chat_history = []

    system_prompt = {
        "role": "system",
        "content": "You are a helpful data insight assistant for a movie database. Your role is to help users get insights from movie data."
    }

    # Combine chat history with new user input
    messages = [system_prompt] + chat_history + [
        {
            "role": "user",
            "content": user_input
        },
    ]

    # Send user input and tools to the model
    response = client.responses.create(
        model="gpt-4.1-nano",
        tools=tools,
        input=messages,
    )

    # Handle any function calls returned by the model
    messages += response.output
    for item in response.output:
        if item.type == "function_call":
            if item.name == "query_database":
                print(f"Function call used, function - query_database")
                st.session_state.logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Function call used, function - query_database")

                args = json.loads(item.arguments)
                result = query_database(args["query"])
            elif item.name == "create_github_ticket":
                print(f"Function call used, function - create_github_ticket")
                args = json.loads(item.arguments)
                result = create_github_ticket(args["title"], args["description"], args.get("labels", []))

            # Provide function call results to the model
            messages.append({
                "type": "function_call_output",
                "call_id": item.call_id,
                "output": json.dumps(result)
            })

    # Ask model to generate final user-facing response
    final_response = client.responses.create(
        model="gpt-4.1-nano",
        instructions="Respond to the user using the database result or ticket result",
        input=messages,
    )
    return final_response.output_text

# print("Agent output:\n")
# print(final_response.output_text)