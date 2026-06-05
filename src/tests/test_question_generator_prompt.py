from src.agents.question_generator.prompt import independent_question_prompt, dependent_question_prompt
from src.models.jd_model import JobDescription
from src.models.plan_model import Phase, Topic
from src.models.states.phase_summary import PhaseSummary
from src.models.states.turn import Turn
from src.models.states.metrics import Metrics
from src.models.util_model import Emp_Type, Loc_Type

def test_independent_question_prompt_contains_updated_rules():
    # Setup dummy objects
    phase_summary = PhaseSummary(
        phase_summary_id="ps_1",
        phase_name="Core Technical",
        summary="Candidate knows Python basics."
    )
    topic = Topic(
        topic_id="t_1",
        topic="Databases",
        source="resume",
        weight=1.0,
        max_question_count=3
    )
    phase = Phase(
        phase_id="p_1",
        name="Core Technical",
        objective="Verify databases knowledge",
        weight=1.0,
        topics=[topic]
    )
    jd = JobDescription(
        jd_id="jd_1",
        job_title="Backend Engineer",
        job_type=Emp_Type.full_time,
        loc_type=Loc_Type.remote,
        min_experience=2.0,
        responsibilities=["Develop APIs"],
        required_qualification="BS CS",
        required_skills=["Python", "SQL"]
    )
    metrics = Metrics(
        QAR=1.0,
        TDS=1.0,
        ACS=1.0,
        SS=1.0,
        CCS=1.0,
        FARQ=1.0,
        RFD=1.0,
        RFD_flags=[]
    )
    turn = Turn(
        chat_id="c_1",
        question="What database experience do you have?",
        response="I have used Postgres and Redis.",
        metrics=metrics,
        phase_name="Core Technical",
        topic_id="t_1"
    )

    messages = independent_question_prompt(
        previous_phase_summaries=[phase_summary],
        user_summary="Enthusiastic developer",
        previous_k_turns=[turn],
        jd=jd,
        phase=phase,
        topic=topic,
        router_reason="TOPIC CHANGED"
    )

    assert len(messages) == 2
    system_message = messages[0].content

    # Assert new independent instructions are in the prompt
    assert "The question itself must NOT require the candidate's last answer" in system_message
    assert "You MAY (and should) open with a brief 1-2 sentence acknowledgment" in system_message
    assert "Your response MUST have exactly two parts, in this order:" in system_message
    assert "1. BRIDGE (1–2 sentences): Naturally acknowledge" in system_message
    assert "2. QUESTION (1 sentence): The next interview question" in system_message


def test_dependent_question_prompt_contains_updated_rules():
    # Setup dummy objects
    phase_summary = PhaseSummary(
        phase_summary_id="ps_1",
        phase_name="Core Technical",
        summary="Candidate knows Python basics."
    )
    topic = Topic(
        topic_id="t_1",
        topic="Databases",
        source="resume",
        weight=1.0,
        max_question_count=3
    )
    phase = Phase(
        phase_id="p_1",
        name="Core Technical",
        objective="Verify databases knowledge",
        weight=1.0,
        topics=[topic]
    )
    jd = JobDescription(
        jd_id="jd_1",
        job_title="Backend Engineer",
        job_type=Emp_Type.full_time,
        loc_type=Loc_Type.remote,
        min_experience=2.0,
        responsibilities=["Develop APIs"],
        required_qualification="BS CS",
        required_skills=["Python", "SQL"]
    )
    metrics = Metrics(
        QAR=1.0,
        TDS=1.0,
        ACS=1.0,
        SS=1.0,
        CCS=1.0,
        FARQ=1.0,
        RFD=1.0,
        RFD_flags=[]
    )
    turn = Turn(
        chat_id="c_1",
        question="What database experience do you have?",
        response="I have used Postgres and Redis.",
        metrics=metrics,
        phase_name="Core Technical",
        topic_id="t_1"
    )

    messages = dependent_question_prompt(
        current_phase_summary=phase_summary,
        previous_k_turns=[turn],
        user_summary="Enthusiastic developer",
        jd=jd,
        phase=phase,
        router_reason="PROBE"
    )

    assert len(messages) == 2
    system_message = messages[0].content

    # Assert new dependent instructions are in the prompt
    assert "CONVERSATION FLOW (MANDATORY):" in system_message
    assert "Before asking your question, open with 1–2 sentences that acknowledge something specific" in system_message
    assert "Your response MUST have exactly two parts, in this order:" in system_message
    assert "1. BRIDGE (1–2 sentences): Acknowledge something specific from the candidate's prior answer" in system_message
    assert "2. QUESTION (1 sentence): The follow-up question" in system_message
