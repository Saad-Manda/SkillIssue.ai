from langchain_core.messages import AIMessage
from langchain_core.output_parsers import JsonOutputParser

from ..llm import get_llm
from ..session_logging import log_agent_error, log_agent_event, log_agent_start
from .prompt import planner_prompt
from ...models.states.states import SystemState
from ...models.plan_model import Plan

llm = get_llm("planner")


def planner_node(system_state: SystemState) -> SystemState:
    """
    Production node to generate full plan which
    represents the flow of the interview.
    """
    session_id = system_state.session_id
    print(f"[planner] start session_id={session_id}")
    log_agent_start("planner", session_id, system_state)

    messages = planner_prompt(system_state)
    log_agent_event(session_id, "planner", "prompt_built", messages=messages)

    parser = JsonOutputParser(pydantic_object=Plan)

    try:
        print(f"[planner] invoking llm messages={len(messages)}")
        response: AIMessage = llm.invoke(messages)
        preview = (response.content or "")[:120].replace("\n", "\\n")
        print(f"[planner] llm_response_preview={preview}")
        log_agent_event(session_id, "planner", "llm_response", response=response)
        
        parsed_data = parser.parse(response.content)
        plan = Plan.model_validate(parsed_data)
    except Exception as e:
        print(f"[planner] Error in LLM invocation: {e}")
        log_agent_error(
            session_id,
            "planner",
            e,
            messages=messages,
        )
        raise
    
    system_state.plan = plan
    print(f"[planner] done phases={len(plan.phase) if getattr(plan, 'phase', None) else 0}")
    log_agent_event(session_id, "planner", "done", updated_state=system_state)

    return system_state
