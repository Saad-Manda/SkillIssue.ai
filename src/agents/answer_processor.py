from .agent_utils.states import GlobalState


def answer_processor_node(state: GlobalState):
    # This is a placeholder for the answer processing logic.
    # In a real-world scenario, you would analyze the user's answer,
    # evaluate it against some metrics, and decide on the next step.

    # For now, we just print the answer and do nothing.
    user_answer = state.get("recent_turns", [{}])[-1].get("answer")
    print(f"User answer: {user_answer}")

    return {}
