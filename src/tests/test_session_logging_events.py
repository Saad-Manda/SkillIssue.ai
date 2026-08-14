import json
from unittest.mock import Mock, patch

from src.agents.session_logging import log_agent_event


def test_log_agent_event_publishes_minimal_fields():
    mock_publish = Mock()
    with patch("src.agents.session_logging.session_store") as mock_store:
        mock_store.client.publish = mock_publish
        log_agent_event("sess1", "router", "start", foo="bar")

    assert mock_publish.call_count == 1
    channel, payload = mock_publish.call_args[0]
    assert channel == "session:sess1:events"
    data = json.loads(payload)
    assert set(data.keys()) == {"session_id", "agent", "event", "timestamp"}
    assert data["session_id"] == "sess1"
    assert data["agent"] == "router"
    assert data["event"] == "start"


def test_log_agent_event_swallows_publish_errors():
    with patch("src.agents.session_logging.session_store") as mock_store:
        mock_store.client.publish = Mock(side_effect=Exception("redis down"))
        log_agent_event("sess1", "router", "start", foo="bar")  # must not raise
