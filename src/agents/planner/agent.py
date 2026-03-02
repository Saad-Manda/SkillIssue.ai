from langchain_core.messages import AIMessage

from ..llm import llm
from .prompt import planner_prompt
from ...models.states.states import SystemState
from ...models.plan_model import Plan


def planner_node(system_state: SystemState) -> SystemState:
    """
    Production node to generate full plan which
    represents the flow of the interview.
    """

    print(f"[planner] start session_id={system_state.session_id}")

    messages = planner_prompt(system_state)

    try:
        print(f"[planner] invoking llm messages={len(messages)}")
        response: AIMessage = llm.invoke(messages)
        preview = (response.content or "")[:120].replace("\n", "\\n")
        print(f"[planner] llm_response_preview={preview}")
        plan = Plan.model_validate_json(response.content)
    except Exception as e:
        print(f"[planner] Error in LLM invocation: {e}")
        raise
    
    system_state.plan = plan
    print(f"[planner] done phases={len(plan.phase) if getattr(plan, 'phase', None) else 0}")

    return system_state