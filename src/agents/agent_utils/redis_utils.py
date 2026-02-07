from typing import Dict, List

from langchain_core.messages import BaseMessage, messages_to_dict

from .redis_session import session_store


def start_new_interview(
    session_id: str, user_data: dict, jd_data: dict, summary: str, max_turns: int = 5
):
    """
    Initializes a new interview session in Redis.
    Must be called BEFORE invoking the graph for the first time.
    """
    print(f"---INITIALIZING SESSION: {session_id}---")

    # 1. Define the Initial State
    # This matches the GlobalState structure but formatted for JSON storage
    initial_state = {
        "session_id": session_id,
        # Store these as dicts so they are JSON serializable
        "current_user": user_data,
        "current_jd": jd_data,
        "user_summary": summary,
        "recent_turns": [],
        "turn_count": 0,
        "max_turns": max_turns,
        "store_count": 1,
        "interview_phase": "introduction",  # We always start here
        "next_question": None,
        # Serialize empty list explicitly
        "chat_history": [],
        "final_report": None,
    }

    # 2. Save to Redis
    # The session_store.set method handles the json.dumps()
    session_store.set(session_id, initial_state)

    print(f"Session {session_id} created in Redis.")
