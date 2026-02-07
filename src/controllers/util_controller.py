
from ..models.jd_model import JobDescription
from langchain_core.messages import messages_from_dict


def _hydrate_messages(raw):
    if isinstance(raw, list):
        try:
            return messages_from_dict(raw)
        except Exception:
            return []
    return []


def _normalize_jd(jd: JobDescription) -> dict:
    jd_data = jd.model_dump()
    jd_data["title"] = jd_data.get("job_title", "")
    jd_data["skills"] = jd_data.get("required_skills", [])
    return jd_data



