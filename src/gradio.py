import gradio as gr
from .controllers.init_controller import start_session
from .controllers.question_gen_controller import submit_answer






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
