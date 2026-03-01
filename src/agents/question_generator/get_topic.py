def get_independent_topic(plan, prev_phase, prev_topic_id):

    for j, phase in enumerate(plan.phase):
            if phase.name is prev_phase:
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