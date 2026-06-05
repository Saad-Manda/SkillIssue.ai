import unittest
from unittest.mock import MagicMock, patch
from src.agents.question_generator.get_topic import get_next_topic
from src.agents.router.agent import router_node
from src.agents.question_generator.agent import question_generator_node
from src.models.plan_model import Plan, Phase, Topic
from src.models.states.states import SystemState
from src.models.states.turn import Turn


class TestTerminationLogic(unittest.TestCase):
    def setUp(self):
        # Patch the LLM to prevent any real API calls
        self.llm_patcher = patch("src.agents.llm.llm")
        self.mock_llm = self.llm_patcher.start()
        self.mock_llm.invoke.return_value = MagicMock(content="Mocked Question")

        # Create a simple 2-phase, 2-topic plan
        topic_1_1 = Topic(
            topic_id="topic-1-1",
            topic="Topic 1.1",
            source="test",
            weight=1.0,
            max_question_count=2
        )
        topic_1_2 = Topic(
            topic_id="topic-1-2",
            topic="Topic 1.2",
            source="test",
            weight=1.0,
            max_question_count=2
        )
        phase_1 = Phase(
            phase_id="phase-1",
            name="Phase 1",
            objective="Obj 1",
            weight=1.0,
            topics=[topic_1_1, topic_1_2]
        )

        topic_2_1 = Topic(
            topic_id="topic-2-1",
            topic="Topic 2.1",
            source="test",
            weight=1.0,
            max_question_count=2
        )
        topic_2_2 = Topic(
            topic_id="topic-2-2",
            topic="Topic 2.2",
            source="test",
            weight=1.0,
            max_question_count=2
        )
        phase_2 = Phase(
            phase_id="phase-2",
            name="Phase 2",
            objective="Obj 2",
            weight=1.0,
            topics=[topic_2_1, topic_2_2]
        )

        self.plan = Plan(phase=[phase_1, phase_2])

    def tearDown(self):
        self.llm_patcher.stop()

    def create_mock_state(self, current_topic_id, current_phase_name, current_topic_question_count, current_turn_status="NORMAL"):
        return SystemState.model_construct(
            session_id="test-session",
            user=MagicMock(),
            user_summary="test summary",
            jd=MagicMock(),
            current_question="some Q",
            is_curr_question_independent=True,
            current_response="some response",
            plan=self.plan,
            current_topic_id=current_topic_id,
            current_topic_question_count=current_topic_question_count,
            current_phase_name=current_phase_name,
            current_turn_status=current_turn_status,
            min_topics=1,
            max_topics=5,
            final_report="",
            should_generate_report=False
        )

    def test_get_next_topic_bounds(self):
        # Test normal next topic (same phase)
        phase_idx, topic_idx = get_next_topic(self.plan, "Phase 1", "topic-1-1")
        self.assertEqual(phase_idx, 0)
        self.assertEqual(topic_idx, 1)

        # Test move to next phase
        phase_idx, topic_idx = get_next_topic(self.plan, "Phase 1", "topic-1-2")
        self.assertEqual(phase_idx, 1)
        self.assertEqual(topic_idx, 0)

        # Test out of bounds (last topic of last phase)
        phase_idx, topic_idx = get_next_topic(self.plan, "Phase 2", "topic-2-2")
        self.assertIsNone(phase_idx)
        self.assertIsNone(topic_idx)

    def test_router_node_non_final_topic(self):
        # Test router behavior when max questions reached on a NON-final topic
        system_state = self.create_mock_state(
            current_topic_id="topic-1-1",
            current_phase_name="Phase 1",
            current_topic_question_count=2,  # max_question_count is 2
        )

        updated_state = router_node(system_state)
        self.assertFalse(updated_state.should_generate_report)
        self.assertEqual(updated_state.current_turn_status, "TOPIC CHANGED")
        self.assertTrue(updated_state.is_curr_question_independent)

    def test_router_node_final_topic(self):
        # Test router behavior when max questions reached on the FINAL topic of the final phase
        system_state = self.create_mock_state(
            current_topic_id="topic-2-2",
            current_phase_name="Phase 2",
            current_topic_question_count=2,  # max_question_count is 2
        )

        updated_state = router_node(system_state)
        self.assertTrue(updated_state.should_generate_report)
        # Verify it does not set TOPIC CHANGED and returns early
        self.assertNotEqual(updated_state.current_turn_status, "TOPIC CHANGED")

    @patch("src.agents.question_generator.agent.session_store")
    def test_question_generator_node_sentinel(self, mock_session_store):
        # Test question generator behavior when sentinel (None, None) is hit
        # We need to mock session_store.get() because it's called in question_generator_node
        turn = Turn.model_construct(
            chat_id="test-chat",
            question="Q?",
            response="A",
            phase_name="Phase 2",
            topic_id="topic-2-2",
            metrics=MagicMock()
        )
        mock_session_state = {
            "chat_history": [turn],
            "phase_summary": []
        }
        mock_session_store.get.return_value = mock_session_state

        system_state = self.create_mock_state(
            current_topic_id="topic-2-2",
            current_phase_name="Phase 2",
            current_topic_question_count=0,
            current_turn_status="TOPIC CHANGED"
        )

        updated_state = question_generator_node(system_state)
        self.assertTrue(updated_state.should_generate_report)
