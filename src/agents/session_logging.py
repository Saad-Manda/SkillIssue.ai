import json
import logging
import re
from pathlib import Path
from threading import Lock
from typing import Any

from langchain_core.messages import BaseMessage
from pydantic import BaseModel


_LOGGER_CACHE: dict[str, logging.Logger] = {}
_LOGGER_LOCK = Lock()


def _safe_session_id(session_id: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9._-]", "_", str(session_id))
    return safe or "unknown_session"


def _log_dir() -> Path:
    repo_root = Path(__file__).resolve().parents[2]
    path = repo_root / "logs" / "interviews"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_session_logger(session_id: str) -> logging.Logger:
    safe_session_id = _safe_session_id(session_id)

    with _LOGGER_LOCK:
        existing = _LOGGER_CACHE.get(safe_session_id)
        if existing is not None:
            return existing

        logger = logging.getLogger(f"interview.{safe_session_id}")
        logger.setLevel(logging.INFO)
        logger.propagate = False

        if not logger.handlers:
            file_path = _log_dir() / f"{safe_session_id}.log"
            handler = logging.FileHandler(file_path, encoding="utf-8")
            handler.setFormatter(
                logging.Formatter("%(message)s")
            )
            logger.addHandler(handler)

        _LOGGER_CACHE[safe_session_id] = logger
        return logger


def _to_loggable(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return _to_loggable(value.model_dump())

    if isinstance(value, BaseMessage):
        return {
            "type": value.type,
            "content": value.content,
            "name": getattr(value, "name", None),
            "additional_kwargs": _to_loggable(value.additional_kwargs),
            "response_metadata": _to_loggable(getattr(value, "response_metadata", {})),
        }

    if isinstance(value, dict):
        return {str(k): _to_loggable(v) for k, v in value.items()}

    if isinstance(value, (list, tuple, set)):
        return [_to_loggable(v) for v in value]

    if isinstance(value, (str, int, float, bool)) or value is None:
        return value

    if hasattr(value, "model_dump"):
        try:
            return _to_loggable(value.model_dump())
        except Exception:
            return repr(value)

    return repr(value)


def log_agent_event(session_id: str, agent: str, event: str, **payload: Any) -> None:
    logger = get_session_logger(session_id)
    serialized = _to_loggable(payload)
    pretty_payload = json.dumps(
        serialized,
        ensure_ascii=False,
        default=str,
        indent=2,
    )
    logger.info(
        "[%s] %s |\n%s",
        agent,
        event,
        pretty_payload,
    )


def log_agent_start(agent: str, session_id: str, system_state: Any) -> None:
    log_agent_event(session_id, agent, "start", system_state=system_state)


def log_agent_error(
    session_id: str, agent: str, error: Exception, **payload: Any
) -> None:
    details = {
        "error_type": type(error).__name__,
        "error_message": str(error),
    }
    details.update(payload)
    log_agent_event(session_id, agent, "error", **details)
