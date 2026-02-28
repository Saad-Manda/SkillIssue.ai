from ..llm import llm
from .prompt import planner_prompt
from ...models.states.states import SystemState

def planner_node(system_state: SystemState) -> SystemState:
    """
    Production node to generate full plan which 
    represents the flow of the interview.
    """

    print(f"---GENERATING PLAN---")

    messages = planner_prompt(system_state)

    try:
        response = llm.invoke(messages)
        plan = response.content
    except Exception as e:
        print(f"Error in LLM invocation: {e}")


    system_state.plan = plan

    return system_state