from unittest.mock import MagicMock, patch

from src.agents.question_generator.prompt import topic_transition_prompt, dependent_question_prompt
from src.models.jd_model import JobDescription
from src.models.plan_model import Phase, Topic
from src.models.states.phase_summary import PhaseSummary
from src.models.states.turn import Turn
from src.models.states.metrics import Metrics
from src.models.util_model import Emp_Type, Loc_Type


def test_topic_transition_prompt_contains_updated_rules():
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
        QAR=1.0, TDS=1.0, ACS=1.0, SS=1.0, CCS=1.0, FARQ=1.0, RFD=1.0, RFD_flags=[]
    )
    turn = Turn(
        chat_id="c_1",
        question="What database experience do you have?",
        response="I have used Postgres and Redis.",
        metrics=metrics,
        phase_name="Core Technical",
        topic_id="t_1"
    )

    messages = topic_transition_prompt(
        previous_phase_summaries=[phase_summary],
        user_summary="Enthusiastic developer",
        previous_k_turns=[turn],
        jd=jd,
        phase=phase,
        topic=topic,
        router_intent="advance_topic",
    )

    assert len(messages) == 2
    system_message = messages[0].content

    assert "BRANCH MODE: TOPIC TRANSITION" in system_message
    assert "Your response MUST have exactly two parts, in this order:" in system_message
    assert "1. BRIDGE (1–2 sentences): Naturally acknowledge" in system_message
    assert "2. QUESTION (1 sentence): The next interview question" in system_message


def test_dependent_question_prompt_contains_updated_rules():
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
        QAR=1.0, TDS=1.0, ACS=1.0, SS=1.0, CCS=1.0, FARQ=1.0, RFD=1.0, RFD_flags=[]
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
        topic=topic,
        router_intent="dependent_followup",
        router_focus="Postgres sharding"
    )

    assert len(messages) == 2
    system_message = messages[0].content

    assert "CONVERSATION FLOW (MANDATORY):" in system_message
    assert "Before asking your question, open with 1–2 sentences that acknowledge something specific" in system_message
    assert "Your response MUST have exactly two parts, in this order:" in system_message
    assert "1. BRIDGE (1–2 sentences): Acknowledge something specific from the candidate's prior answer" in system_message
    assert "2. QUESTION (1 sentence): The question." in system_message
    assert "BRANCH MODE: DEPENDENT FOLLOW-UP" in system_message
    assert "Postgres sharding" in system_message


# ---------------------------------------------------------------------------
# Shared fixture factory
# ---------------------------------------------------------------------------

def _make_fixtures():
    """Shared fixture factory to avoid repeating boilerplate across tests."""
    phase_summary = PhaseSummary(
        phase_summary_id="ps_1",
        phase_name="Core Technical",
        summary="Candidate knows Python basics."
    )
    prev_topic = Topic(
        topic_id="t_prev",
        topic="Databases",
        source="resume",
        weight=1.0,
        max_question_count=2
    )
    new_topic = Topic(
        topic_id="t_new",
        topic="System Design",
        source="jd",
        weight=1.0,
        max_question_count=3
    )
    phase = Phase(
        phase_id="p_1",
        name="Core Technical",
        objective="Assess engineering depth",
        weight=1.0,
        topics=[prev_topic, new_topic]
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
        QAR=0.8, TDS=0.7, ACS=0.8, SS=0.7, CCS=0.9, FARQ=0.8, RFD=0.0, RFD_flags=[]
    )
    last_turn = Turn(
        chat_id="c_last",
        question="How do you choose between SQL and NoSQL?",
        response="I prefer SQL for relational data, NoSQL for unstructured or high-write workloads.",
        metrics=metrics,
        phase_name="Core Technical",
        topic_id="t_prev"
    )
    return phase_summary, new_topic, phase, jd, last_turn


def test_question_generator_topic_changed_passes_only_last_turn():
    """
    Integration guard: when TOPIC CHANGED fires, question_generator_node must
    call topic_transition_prompt with exactly one turn (the last one).
    The prompt must NOT receive an empty context.
    """
    from src.agents.question_generator.agent import question_generator_node
    from src.models.plan_model import Plan, Phase, Topic
    from src.models.states.states import SystemState
    from src.models.states.turn import Turn
    from src.models.states.metrics import Metrics

    metrics = Metrics(QAR=0.8, TDS=0.7, ACS=0.8, SS=0.7, CCS=0.9, FARQ=0.8, RFD=0.0, RFD_flags=[])
    last_turn = Turn(
        chat_id="c_last",
        question="How do you shard a database?",
        response="I use consistent hashing for sharding.",
        metrics=metrics,
        phase_name="Phase 1",
        topic_id="topic-1-1"
    )

    topic_1_1 = Topic(topic_id="topic-1-1", topic="Databases", source="test", weight=1.0, max_question_count=2)
    topic_1_2 = Topic(topic_id="topic-1-2", topic="System Design", source="test", weight=1.0, max_question_count=2)
    phase_1 = Phase(phase_id="phase-1", name="Phase 1", objective="Obj 1", weight=1.0, topics=[topic_1_1, topic_1_2])
    plan = Plan(phase=[phase_1])

    mock_session_state = {
        "chat_history": [last_turn.model_dump()],
        "phase_summary": []
    }

    captured_kwargs = {}

    def capture_prompt(**kwargs):
        captured_kwargs.update(kwargs)
        return [MagicMock(content="sys"), MagicMock(content="human")]

    system_state = SystemState.model_construct(
        session_id="test-session",
        user=MagicMock(),
        user_summary="test summary",
        jd=MagicMock(),
        current_question="some Q",
        is_curr_question_independent=True,
        current_response="some response",
        plan=plan,
        current_topic_id="topic-1-1",
        current_topic_question_count=2,  # k == max_question_count -> TOPIC CHANGED
        current_phase_name="Phase 1",
        router_intent="advance_topic",
        min_topics=1,
        max_topics=5,
        final_report="",
        should_generate_report=False,
        turns_in_current_phase=[]
    )

    with patch("src.agents.question_generator.agent.session_store") as mock_store, \
         patch("src.agents.question_generator.agent.topic_transition_prompt", side_effect=capture_prompt), \
         patch("src.agents.question_generator.agent.llm") as mock_llm:
        mock_store.get.return_value = mock_session_state
        mock_llm.invoke.return_value = MagicMock(content="Mocked transition question")

        question_generator_node(system_state)

    # Exactly one turn must be passed (option a: last turn only)
    turns_passed = captured_kwargs.get("previous_k_turns", [])
    assert len(turns_passed) == 1, \
        f"Expected exactly 1 bridge turn, got {len(turns_passed)}"

    # That turn must be the candidate's last one
    assert turns_passed[0].chat_id == "c_last", \
        "The bridge turn must be the most recent turn from chat history"
