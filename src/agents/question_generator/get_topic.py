def get_next_topic(plan, prev_phase, prev_topic_id):

    new_phase_idx = None
    new_topic_idx = None

    for j, phase in enumerate(plan.phase):
        if phase.name == prev_phase:
            for i, topic in enumerate(phase.topics):
                if topic.topic_id == prev_topic_id:
                    new_topic_idx = i+1
                    if new_topic_idx >= len(phase.topics):
                        new_topic_idx = None
                        break
                    else:
                        new_phase_idx = j
                        break

            if new_topic_idx is None:
                new_phase_idx = j+1
                new_topic_idx = 0

    return new_phase_idx, new_topic_idx


def get_current_topic(plan, current_phase, current_topic_id):

    found=False
    current_topic = None
    for phase in (plan.phase):
        if phase.name == current_phase:
            for topic in (phase.topics):
                if topic.topic_id == current_topic_id:
                    current_topic = topic
                    found=True
                    break
            if found:
                break
                

    return current_topic