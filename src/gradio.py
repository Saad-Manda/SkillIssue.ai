import gradio as gr

from .controllers.init_controller import start_session
from .controllers.question_gen_controller import submit_answer
from .controllers.report_controller import print_report


def _toggle_report_button(turn_count: int, max_turns: int):
    return gr.update(visible=turn_count >= max_turns)


def _show_report_modal():
    return gr.update(visible=True)


def _hide_report_modal():
    return gr.update(visible=False)


with gr.Blocks(title="SkillIssue.ai") as demo:
    gr.HTML(
        """
        <style>
          #report-modal {
            position: fixed;
            inset: 0;
            background: rgba(0, 0, 0, 0.55);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 9999;
          }
          #report-modal .modal-card {
            width: min(900px, 92vw);
            max-height: 85vh;
            background: #ffffff;
            border-radius: 14px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
            display: flex;
            flex-direction: column;
          }
          #report-modal .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 14px 18px;
            border-bottom: 1px solid #e6e6e6;
            font-weight: 600;
          }
          #report-modal .modal-body {
            padding: 18px;
            overflow: auto;
          }
        </style>
        """
    )
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
    max_turns_input = gr.Slider(1, 20, value=1, step=1, label="Max Turns")

    session_id_state = gr.State("")
    chat_state = gr.State([])

    chat_ui = gr.Chatbot(label="Interview Chat", height=360)
    answer_input = gr.Textbox(label="Your Answer")
    start_btn = gr.Button("Start Interview")
    send_btn = gr.Button("Send Answer")
    report_btn = gr.Button("Generate Report", visible=False)

    turn_count_output = gr.Number(label="Turn Count", value=0, precision=0)
    store_count_output = gr.Number(label="Store Count", value=0, precision=0)
    with gr.Group(visible=False, elem_id="report-modal") as report_modal:
        with gr.Column(elem_classes=["modal-card"]):
            with gr.Row(elem_classes=["modal-header"]):
                gr.Markdown("Final Report")
                close_btn = gr.Button("Close")
            with gr.Column(elem_classes=["modal-body"]):
                report_output = gr.Markdown()

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

    turn_count_output.change(
        fn=_toggle_report_button,
        inputs=[turn_count_output, max_turns_input],
        outputs=[report_btn],
    )

    report_btn.click(
        fn=print_report,
        inputs=[session_id_state],
        outputs=[report_output],
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
