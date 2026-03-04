import json
import uuid

import gradio as gr

from .agents.app import app
from .models.user_model import User
from .models.jd_model import JobDescription
from .models.plan_model import Plan
from .models.states.states import SystemState


def _toggle_report_button(turn_count: int, interview_length: str):
    length_to_turns = {
        "short": 5,
        "medium": 10,
        "deep_dive": 15,
    }
    max_turns = length_to_turns.get(interview_length, 10)
    return gr.update(visible=turn_count >= max_turns)


def _show_report_modal():
    return gr.update(visible=True)


def _hide_report_modal():
    return gr.update(visible=False)


def _parse_json(text: str) -> dict:
    if not text:
        return {}
    return json.loads(text)


def _build_initial_state(
    session_id: str,
    user: User,
    jd: JobDescription,
    interview_length: str,
) -> SystemState:
    length_to_topics = {
        "short": (5, 10),
        "medium": (10, 15),
        "deep_dive": (15, 20),
    }
    min_topics, max_topics = length_to_topics.get(interview_length, (10, 15))

    return SystemState(
        session_id=session_id,
        user=user,
        user_summary="",
        jd=jd,
        current_question="",
        is_curr_question_independent=True,
        current_response="",
        plan=Plan.model_construct(),
        current_topic_id="",
        current_topic_question_count=0,
        current_phase_name="introduction",
        current_turn_status="START",
        min_topics=min_topics,
        max_topics=max_topics,
        final_report="",
    )


def _run_graph(state: SystemState, *, resume: bool = False) -> SystemState:
    """
    Run or resume the LangGraph interview flow.

    - When resume=False (initial call), we start the graph from the entry node.
    - When resume=True, we continue from the last interrupted node for this
      session_id, merging in the updated fields from `state`.
    """
    
    print(f"[_run_graph] resume={resume}, thread_id={state.session_id!r}") 
    # Base config for this session
    config = {
        "configurable": {"thread_id": state.session_id},
        "recursion_limit": 50,
    }

    if resume:
        app.update_state(config, {"current_response": state.current_response})
        input_payload = None

    else:
        input_payload = state

    result = app.invoke(input_payload, config=config)
    return SystemState.model_validate(result)


def start_session(user_json: str, jd_json: str, interview_length: str):
    try:
        user_dict = _parse_json(user_json)
        jd_dict = _parse_json(jd_json)
        user = User(**user_dict)
        jd = JobDescription(**jd_dict)
    except Exception as e:
        error = f"Failed to parse input: {e}"
        chat = [{"role": "assistant", "content": error}]
        return "", None, chat, 0, 0

    session_id = str(uuid.uuid4())
    print(f"[start_session] created session_id={session_id!r}")
    initial_state = _build_initial_state(session_id, user, jd, interview_length)
    # First graph run: start from entry node (user_summarizer/planner/etc.).
    state = _run_graph(initial_state, resume=False)

    chat = []
    if state.current_question:
        chat.append({"role": "assistant", "content": state.current_question})

    turn_count = 0
    store_count = 1 if chat else 0

    return session_id, state, chat, turn_count, store_count


def submit_answer(session_id: str, state: SystemState | None, answer: str, chat):
    print(f"[submit_answer] session_id param={session_id!r}, state.session_id={state.session_id if state else 'STATE IS NONE'!r}") 

    if not session_id or state is None:
        return state, (chat or []), 0, 0

    chat = chat or []
    if answer:
        chat.append({"role": "user", "content": answer})

    updated_state = state.model_copy(update={"current_response": answer})
    # Resume the graph from the last interruption (just after question generation),
    # starting at the `phase_summarizer` node for this session.
    next_state = _run_graph(updated_state, resume=True)

    if next_state.current_question:
        chat.append({"role": "assistant", "content": next_state.current_question})

    turn_count = sum(
        1 for msg in chat if isinstance(msg, dict) and msg.get("role") == "assistant"
    )
    store_count = turn_count

    return next_state, chat, turn_count, store_count


def print_report(state: SystemState | None, session_id: str):
    if state is None:
        return "No report available yet.", None
    
    app.update_state(
        {"configurable": {"thread_id": session_id}},
        {"should_generate_report": True}
    )
    updated_state = state.model_copy(update={"should_generate_report": True})
    final_state = _run_graph(updated_state, resume=True)
    return final_state.final_report, final_state


with gr.Blocks(title="SkillIssue.ai") as demo:
    gr.HTML(
        """
        <style>
          body, .gradio-container {
            background: radial-gradient(circle at top, #0f172a 0, #020617 55%, #000 100%);
            color: #e5e7eb;
          }
          .si-header {
            text-align: center;
            font-size: 1.6rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: #e5e7eb;
          }
          .si-subtitle {
            text-align: center;
            font-size: 0.95rem;
            color: #9ca3af;
            margin-bottom: 1.5rem;
          }
          .si-panel {
            background: rgba(15, 23, 42, 0.94);
            border-radius: 18px;
            border: 1px solid rgba(51, 65, 85, 0.9);
            box-shadow: 0 24px 60px rgba(15, 23, 42, 0.9);
            padding: 18px 18px 14px 18px;
          }
          .si-panel h3 {
            margin: 0 0 0.6rem 0;
            font-size: 0.95rem;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            color: #9ca3af;
          }
          .si-strong {
            color: #e5e7eb;
            font-weight: 600;
          }
          .si-primary-btn button {
            background: linear-gradient(135deg, #2563eb, #1d4ed8);
            color: #e5e7eb;
            border-radius: 999px;
            border: none;
            font-weight: 600;
          }
          .si-primary-btn button:hover {
            background: linear-gradient(135deg, #1d4ed8, #1e40af);
          }
          .si-secondary-btn button {
            background: rgba(15, 23, 42, 0.85);
            color: #e5e7eb;
            border-radius: 999px;
            border: 1px solid rgba(75, 85, 99, 0.9);
          }
          .si-secondary-btn button:hover {
            background: rgba(30, 64, 175, 0.35);
          }
          .si-chatbot .wrap {
            background: radial-gradient(circle at top left, #020617 0, #020617 40%, #000 100%);
          }
          .si-chatbot .message.user {
            background: rgba(30, 64, 175, 0.9);
          }
          .si-chatbot .message.bot {
            background: rgba(15, 23, 42, 0.96);
          }
          .si-input textarea {
            background: rgba(15, 23, 42, 0.9);
            border-radius: 14px;
            border: 1px solid rgba(51, 65, 85, 0.9);
            color: #e5e7eb;
          }
          .si-input textarea:focus-visible {
            border-color: #2563eb;
            outline: 1px solid #2563eb;
          }
          #report-modal {
            position: fixed;
            inset: 0;
            background: rgba(15, 23, 42, 0.88);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 9999;
          }
          #report-modal .modal-card {
            width: min(900px, 92vw);
            max-height: 85vh;
            background: #020617;
            border-radius: 18px;
            border: 1px solid rgba(55, 65, 81, 0.85);
            box-shadow: 0 32px 80px rgba(15, 23, 42, 0.95);
            overflow: hidden;
            display: flex;
            flex-direction: column;
          }
          #report-modal .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 14px 18px;
            border-bottom: 1px solid rgba(55, 65, 81, 0.7);
            font-weight: 600;
            color: #e5e7eb;
          }
          #report-modal .modal-body {
            padding: 18px;
            overflow: auto;
            background: radial-gradient(circle at top left, #020617 0, #020617 40%, #000 100%);
          }
        </style>
        """
    )

    gr.Markdown("<div class='si-header'>SkillIssue.ai Interview Studio</div>")
    gr.Markdown(
        "<div class='si-subtitle'>Upload your profile & target role, pick an interview depth, and practice in a realistic, adaptive mock interview.</div>"
    )

    session_id_state = gr.State("")
    system_state_state = gr.State(None)
    chat_state = gr.State([])  # retained for compatibility, unused

    with gr.Row():
        with gr.Column(scale=5, elem_classes=["si-panel"]):
            gr.Markdown("### Candidate & Role")
            user_input = gr.Textbox(
                label="Candidate JSON",
                lines=10,
                elem_classes=["si-input"],
                placeholder='{"id":"user-1","name":"Jane Doe","email":"jane@example.com","education":{"institute_name":"State U","degree":"BSc CS","grade":3.6,"courses":["DSA"],"start_date":"2016-09-01","end_date":"2020-05-15"},"skills":["Python","FastAPI"]}',
            )
            jd_input = gr.Textbox(
                label="Job Description JSON",
                lines=10,
                elem_classes=["si-input"],
                placeholder='{"job_title":"Backend Engineer","job_type":"full_time","loc_type":"remote","location":"Remote","min_experience":3,"responsibilities":["Build APIs"],"required_qualification":"BSc CS","required_skills":["Python","FastAPI"],"preferred_skills":[],"description":"Backend role"}',
            )
            interview_length_input = gr.Radio(
                choices=[
                    ("Short • 5–10 topics", "short"),
                    ("Medium • 10–15 topics", "medium"),
                    ("Deep dive • 15–20 topics", "deep_dive"),
                ],
                value="medium",
                label="Interview length",
            )
            with gr.Row():
                start_btn = gr.Button("Start Interview", elem_classes=["si-primary-btn"])

        with gr.Column(scale=7, elem_classes=["si-panel"]):
            gr.Markdown("### Live Interview")
            chat_ui = gr.Chatbot(label="Interview Chat", height=360, elem_classes=["si-chatbot"])
            answer_input = gr.Textbox(
                label="Your Answer",
                lines=4,
                placeholder="Type your response here...",
                elem_classes=["si-input"],
            )
            with gr.Row():
                send_btn = gr.Button("Send Answer", elem_classes=["si-secondary-btn"])
                report_btn = gr.Button("View Readiness Report", visible=False, elem_classes=["si-secondary-btn"])

            with gr.Row():
                turn_count_output = gr.Number(label="Turns so far", value=0, precision=0)
                store_count_output = gr.Number(label="Internal steps", value=0, precision=0)

    with gr.Group(visible=False, elem_id="report-modal") as report_modal:
        with gr.Column(elem_classes=["modal-card"]):
            with gr.Row(elem_classes=["modal-header"]):
                gr.Markdown("Interview Readiness Report")
                close_btn = gr.Button("Close", elem_classes=["si-secondary-btn"])
            with gr.Column(elem_classes=["modal-body"]):
                report_output = gr.Markdown()

    start_btn.click(
        fn=start_session,
        inputs=[user_input, jd_input, interview_length_input],
        outputs=[session_id_state, system_state_state, chat_ui, turn_count_output, store_count_output],
    )

    send_btn.click(
        fn=submit_answer,
        inputs=[session_id_state, system_state_state, answer_input, chat_ui],
        outputs=[system_state_state, chat_ui, turn_count_output, store_count_output],
    )

    turn_count_output.change(
        fn=_toggle_report_button,
        inputs=[turn_count_output, interview_length_input],
        outputs=[report_btn],
    )

    report_btn.click(
        fn=print_report,
        inputs=[system_state_state, session_id_state],
        outputs=[report_output, system_state_state],
    ).then(
        fn=_show_report_modal,
        outputs=[report_modal],
    )

    close_btn.click(
        fn=_hide_report_modal,
        outputs=[report_modal],
    )


if __name__ == "__main__":
    demo.launch()
