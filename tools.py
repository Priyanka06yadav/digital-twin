import sqlite3
from agents import function_tool
import requests
import os
from dotenv import load_dotenv


@function_tool
def record_user_details(name: str, email:str) -> str:
    """"
    Save visitor's name and email when they want to get in touch
    """

    connection = sqlite3.connect("visitors.db")
    cursor = connection.cursor()

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS visitors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL
    )
""")

    cursor.execute("INSERT INTO visitors (name, email) VALUES (?, ?)", (name, email))
    connection.commit()
    connection.close()

    return f"Contact details recorded for {name} ({email}). We will get in touch with you soon."


@function_tool
def record_unknown_question(question: str) -> str:
    """
    Save a question that the Digital Twin cannot
    answer using the available professional knowledge.
    """

    connection = sqlite3.connect("unknown_questions.db")
    cursor = connection.cursor()

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS unknown_questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT NOT NULL
    )
""")

    cursor.execute("INSERT INTO unknown_questions (question) VALUES (?)", (question,))
    connection.commit()
    connection.close()

    return "The unanswered question has been recorded."

@function_tool
def push_tool(message: str) -> str:
    """
    Send a push notification to the Digital Twin owner
    """

    load_dotenv(override=True)

    pushover_user = os.getenv("PUSHOVER_USER")
    pushover_token = os.getenv("PUSHOVER_TOKEN")

    pushover_url = "https://api.pushover.net/1/messages.json"


    payload = {
        "token": pushover_token,
        "user": pushover_user,
        "message": message
    }

    response = requests.post(pushover_url, data=payload)

    return f"Pushover response status: {response.status_code}"