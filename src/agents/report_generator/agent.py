from langchain_core.messages import HumanMessage, SystemMessage

from ..llm import llm
from ..session_logging import log_agent_error, log_agent_event, log_agent_start
from .prompt import generate_report_prompt
from ...models.states.states import SystemState
from ...models.states.redis_session import parse_chat_history, session_store
from ...models.states.turn import Turn

def report_node(system_state: SystemState) -> SystemState:

    session_id = system_state.session_id
    session_state = session_store.get(session_id)
    log_agent_start("report_generator", session_id, system_state)
    log_agent_event(
        session_id,
        "report_generator",
        "session_store_loaded",
        session_state=session_state,
    )
    print(f"[report_generator] start session_id={session_id}")

    user_summary = system_state.user_summary
    jd = system_state.jd
    raw_history = session_state.get("chat_history", [])
    raw_history = parse_chat_history(raw_history)
    if not isinstance(raw_history, list):
        raw_history = []
    log_agent_event(
        session_id,
        "report_generator",
        "context_prepared",
        user_summary=user_summary,
        jd=jd,
        raw_history=raw_history,
    )
    if raw_history:
        print(
            type(raw_history[0]),
            raw_history[0].model_dump()
            if hasattr(raw_history[0], "model_dump")
            else raw_history[0],
        )
    else:
        print("[report_generator] raw_history is empty")
    # 2. Format Chat History for the LLM
    # Convert stored turns into a readable interview script with metrics
    formatted_transcript = ""
    for msg in raw_history:
        # Normal case: Turn objects from parse_chat_history
        if isinstance(msg, Turn):
            phase = msg.phase_name
            topic_id = msg.topic_id
            question = msg.question
            response_text = msg.response
            metrics = msg.metrics

            plan = system_state.plan
            topic_name = next(
                (t.topic for p in plan.phase if p.name == phase_name for t in p.topics if t.topic_id == topic_id),
                None
            )

            metrics_text = ""
            if metrics is not None:
                try:
                    metrics_dict = metrics.model_dump()
                except AttributeError:
                    metrics_dict = dict(metrics)
                # Build a concise, single-line metrics summary for the LLM
                metrics_pairs = [
                    f"{k}={v}"
                    for k, v in metrics_dict.items()
                    if k not in {"RFD_flags", "STAR_components"}
                ]
                rfd_flags = metrics_dict.get("RFD_flags") or []
                if rfd_flags:
                    metrics_pairs.append(
                        "RFD_flags=" + " | ".join(str(f) for f in rfd_flags)
                    )
                metrics_text = "; ".join(metrics_pairs)

            formatted_transcript += (
                f"[PHASE={phase} TOPIC_ID={topic_id} TOPIC={topic_name}]\n"
                f"[INTERVIEWER]: {question}\n"
                f"[CANDIDATE]: {response_text}\n"
            )
            if metrics_text:
                formatted_transcript += f"[METRICS]: {metrics_text}\n"
            formatted_transcript += "\n"

        # Fallbacks for older / alternative shapes (dicts, LC messages, etc.)
        elif isinstance(msg, dict) and "question" in msg and "response" in msg:
            phase = msg.get("phase_name", "")
            topic_id = msg.get("topic_id", "")
            metrics = msg.get("metrics")

            plan = system_state.plan
            topic_name = next(
                (t.topic for p in plan.phase if p.name == phase_name for t in p.topics if t.topic_id == topic_id),
                None
            )

            metrics_text = ""
            if isinstance(metrics, dict):
                metrics_pairs = [
                    f"{k}={v}"
                    for k, v in metrics.items()
                    if k not in {"RFD_flags", "STAR_components"}
                ]
                rfd_flags = metrics.get("RFD_flags") or []
                if rfd_flags:
                    metrics_pairs.append(
                        "RFD_flags=" + " | ".join(str(f) for f in rfd_flags)
                    )
                metrics_text = "; ".join(metrics_pairs)

            formatted_transcript += (
                f"[PHASE={phase} TOPIC_ID={topic_id}] TOPIC={topic_name}\n"
                f"[INTERVIEWER]: {msg.get('question', '')}\n"
                f"[CANDIDATE]: {msg.get('response', '')}\n"
            )
            if metrics_text:
                formatted_transcript += f"[METRICS]: {metrics_text}\n"
            formatted_transcript += "\n"

        else:
            # Generic role/content fallback
            if isinstance(msg, dict):
                if "role" in msg or "content" in msg:
                    role = msg.get("role", "unknown").upper()
                    content = msg.get("content", "")
                elif (
                    "type" in msg
                    and "data" in msg
                    and isinstance(msg.get("data"), dict)
                ):
                    role = str(msg.get("type", "unknown")).upper()
                    content = msg["data"].get("content", "")
                else:
                    role = "UNKNOWN"
                    content = ""
            else:
                role = getattr(msg, "type", "unknown").upper()
                content = getattr(msg, "content", "")

            formatted_transcript += f"[{role}]: {content}\n\n"

    # 3. Construct the Prompt
    # We use a comprehensive system instruction to define the persona and output format
    system_instruction, user_context_prompt = generate_report_prompt(
        user_summary, jd, formatted_transcript
    )
    log_agent_event(
        session_id,
        "report_generator",
        "prompt_built",
        system_instruction=system_instruction,
        user_context_prompt=user_context_prompt,
        formatted_transcript=formatted_transcript,
    )

    # 5. Invoke LLM
    messages = [
        SystemMessage(content=system_instruction),
        HumanMessage(content=user_context_prompt)
    ]
    report = "## Error\nAn error occurred while generating the report."
    try:
        print(
            f"[report_generator] invoking llm messages={len(messages)} "
            f"transcript_len={len(formatted_transcript)} user_summary_len={len(user_summary or '')}"
        )
        response = llm.invoke(messages)
        report = response.content
        log_agent_event(
            session_id,
            "report_generator",
            "llm_response",
            response=response,
        )
    except Exception as e:
        # Log error here if you have a logger
        print(f"[report_generator] Generation Error: {str(e)}")
        log_agent_error(session_id, "report_generator", e, messages=messages)

    
    system_state.final_report = report
    print(f"[report_generator] done report_len={len(report or '')}")
    log_agent_event(session_id, "report_generator", "done", updated_state=system_state)

    return system_state
