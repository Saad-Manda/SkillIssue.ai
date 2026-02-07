import json

import gradio as gr

from .agents.orchestrator import app
from .models.jd_model import JobDescription
from .models.user_model import User


def run_interview(user_json: str, jd_json: str, max_turns: int):
    user_dict = json.loads(user_json)
    jd_dict = json.loads(jd_json)

    user = User(**user_dict)
    jd = JobDescription(**jd_dict)

    initial_state = {
        "session_id": None,
        "current_user": user,
        "current_jd": jd.model_dump(),
        "user_summary": "",
        "recent_turns": [],
        "turn_count": 0,
        "max_turns": max_turns,
        "store_count": 0,
        "interview_phase": "introduction",
        "next_question": None,
        "chat_history": [],
        "final_report": None,
    }

    result = app.invoke(initial_state)
    return result.get("user_summary", ""), result.get("next_question", "")


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

    summary_output = gr.Textbox(label="User Summary")
    question_output = gr.Textbox(label="Next Question")

    run_btn = gr.Button("Run Interview")
    run_btn.click(
        fn=run_interview,
        inputs=[user_input, jd_input, max_turns_input],
        outputs=[summary_output, question_output],
    )


if __name__ == "__main__":
    demo.launch()
