import json
import uuid

import gradio as gr
from langchain_core.messages import HumanMessage, messages_from_dict, messages_to_dict

from .agents.agent_utils.redis_session import session_store
from .agents.agent_utils.redis_utils import start_new_interview
from .agents.question_generator import question_generator_node
from .agents.summarizer import summarizer_node
from .models.jd_model import JobDescription
from .models.user_model import User


def _hydrate_messages(raw):
    if isinstance(raw, list):
        try:
            return messages_from_dict(raw)
        except Exception:
            return []
    return []


def _normalize_jd(jd: JobDescription) -> dict:
    jd_data = jd.model_dump()
    jd_data["title"] = jd_data.get("job_title", "")
    jd_data["skills"] = jd_data.get("required_skills", [])
    return jd_data


def start_session(user_json: str, jd_json: str, max_turns: int):
    user_dict = json.loads(user_json)
    jd_dict = json.loads(jd_json)

    if isinstance(user_dict, dict) and "user_profile" in user_dict:
        user_dict = user_dict["user_profile"]
    if isinstance(jd_dict, dict) and "jd_profile" in jd_dict:
        jd_dict = jd_dict["jd_profile"]

    user = User(**user_dict)
    jd = JobDescription(**jd_dict)

    summary = summarizer_node({"current_user": user}).get("user_summary", "")

    session_id = str(uuid.uuid4())
    start_new_interview(
        session_id=session_id,
        user_data=user.model_dump(mode="json"),
        jd_data=_normalize_jd(jd),
        summary=summary,
        max_turns=max_turns,
    )

    state = session_store.get(session_id)
    state["chat_history"] = _hydrate_messages(state.get("chat_history"))
    state["current_jd"] = state.get("current_jd", {})
    state["turn_count"] = state.get("turn_count", 0)
    state["max_turns"] = state.get("max_turns", max_turns)

    result = question_generator_node(state)
    next_question = result.get("next_question", "")

    chat = [{"role": "assistant", "content": next_question}]
    latest_state = session_store.get(session_id)

    return (
        session_id,
        chat,
        latest_state.get("turn_count", 0),
        latest_state.get("store_count", 0),
    )


def submit_answer(session_id: str, answer: str, chat):
    if not session_id:
        return chat, 0, 0

    state = session_store.get(session_id)
    if not state:
        return chat, 0, 0

    chat = chat or []
    chat.append({"role": "user", "content": answer})

    recent_turns = state.get("recent_turns", [])
    if recent_turns and recent_turns[-1].get("answer", "") == "":
        recent_turns[-1]["answer"] = answer
    else:
        recent_turns.append({"question": "", "answer": answer, "metrics": {}})

    history_messages = _hydrate_messages(state.get("chat_history"))
    history_messages.append(HumanMessage(content=answer))

    session_store.update(
        session_id,
        recent_turns=recent_turns,
        chat_history=messages_to_dict(history_messages),
    )

    turn_count = state.get("turn_count", 0)
    max_turns = state.get("max_turns", 1)
    if turn_count >= max_turns:
        chat.append({"role": "assistant", "content": "Interview complete."})
        latest_state = session_store.get(session_id)
        return (
            chat,
            latest_state.get("turn_count", 0),
            latest_state.get("store_count", 0),
        )

    state = session_store.get(session_id)
    state["chat_history"] = _hydrate_messages(state.get("chat_history"))
    result = question_generator_node(state)
    next_question = result.get("next_question", "")

    chat.append({"role": "assistant", "content": next_question})
    latest_state = session_store.get(session_id)

    return chat, latest_state.get("turn_count", 0), latest_state.get("store_count", 0)


with gr.Blocks(title="SkillIssue.ai") as demo:
    gr.Markdown("SkillIssue.ai Interview Demo")

    user_input = gr.Textbox(
        label="User JSON",
        lines=12,
        placeholder='{"id":"user-1","name":"Jane Doe","email":"jane@example.com","education":{"institute_name":"State U","degree":"BSc CS","grade":3.6,"courses":["DSA"],"start_date":"2016-09-01","end_date":"2020-05-15"},"skills":["Python","FastAPI"]}',
    )
    jd_input = gr.Textbox(
        label="Job Description JSON",
        lines=12,
        placeholder='{"job_title":"Backend Engineer","job_type":"full_time","loc_type":"remote","location":"Remote","min_experience":3,"responsibilities":["Build APIs"],"required_qualification":"BSc CS","required_skills":["Python","FastAPI"],"preferred_skills":[],"description":"Backend role"}',
    )
    max_turns_input = gr.Slider(1, 5, value=1, step=1, label="Max Turns")

    session_id_state = gr.State("")
    chat_state = gr.State([])

    chat_ui = gr.Chatbot(label="Interview Chat", height=360)
    answer_input = gr.Textbox(label="Your Answer")
    start_btn = gr.Button("Start Interview")
    send_btn = gr.Button("Send Answer")

    turn_count_output = gr.Number(label="Turn Count", value=0, precision=0)
    store_count_output = gr.Number(label="Store Count", value=0, precision=0)

    start_btn.click(
        fn=start_session,
        inputs=[user_input, jd_input, max_turns_input],
        outputs=[session_id_state, chat_ui, turn_count_output, store_count_output],
    )

    send_btn.click(
        fn=submit_answer,
        inputs=[session_id_state, answer_input, chat_ui],
        outputs=[chat_ui, turn_count_output, store_count_output],
    )


if __name__ == "__main__":
    demo.launch()
