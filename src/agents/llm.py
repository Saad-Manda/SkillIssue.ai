from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from ..config import settings
from dotenv import load_dotenv

load_dotenv()

# Mapping of agent names to their preferred Groq key index (1-based)
AGENT_KEY_MAPPING = {
    "user_summarizer": 1,
    "phase_summarizer": 1,
    "planner": 2,
    "metric_calculator": 2,
    "report_generator": 3,
    "router": 3,
    "question_generator": 4,
    "default": 1
}

# Cache for LLM instances to avoid recreating them
_llm_cache = {}

def get_llm(agent_name: str = "default"):
    """
    Returns the appropriate LLM client instance for the specified agent.
    
    If OPENAI_API_KEY is configured, uses OpenAI for all agents.
    Otherwise, if GEMINI_API_KEY (or GOOGLE_API_KEY) is configured, uses Gemini for all agents.
    Otherwise, uses one of 4 Groq API keys based on the agent's preferred slot,
    falling back to other slots in rotation if the preferred key is missing.
    """
    global _llm_cache

    # 1. Check OpenAI Override
    openai_key = settings.OPENAI_API_KEY
    if openai_key:
        cache_key = ("openai", openai_key)
        if cache_key not in _llm_cache:
            model_name = settings.MODEL
            if "gpt" not in model_name.lower():
                # Default fallback model for OpenAI if model setting is currently a Gemini/Groq one
                model_name = "gpt-5-nano"
            print(f"[llm] Initializing OpenAI LLM for {agent_name} using model {model_name}")
            _llm_cache[cache_key] = ChatOpenAI(
                model=model_name,
                api_key=openai_key,
                temperature=0.6
            )
        return _llm_cache[cache_key]

    # 2. Check Gemini Override
    gemini_key = settings.GEMINI_API_KEY
    if gemini_key:
        cache_key = ("gemini", gemini_key)
        if cache_key not in _llm_cache:
            model_name = settings.MODEL
            if "gemini" not in model_name.lower():
                # Default fallback model for Gemini if model setting is currently a Groq one
                model_name = "gemini-3.6-flash"
            print(f"[llm] Initializing Gemini LLM for {agent_name} using model {model_name}")
            _llm_cache[cache_key] = ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=gemini_key,
                temperature=0.6
            )
        return _llm_cache[cache_key]

    # 3. Groq Distribution & Fallback Logic
    groq_keys = [
        settings.GROQ_API_KEY_1,
        settings.GROQ_API_KEY_2,
        settings.GROQ_API_KEY_3,
        settings.GROQ_API_KEY_4
    ]

    # If no numbered Groq keys are configured, check legacy single GROQ_API_KEY
    if not any(groq_keys) and settings.GROQ_API_KEY:
        groq_keys = [settings.GROQ_API_KEY, None, None, None]

    # Determine preferred slot (0-based index)
    preferred_slot = AGENT_KEY_MAPPING.get(agent_name, 1) - 1

    # Try preferred slot, then rotate through the other slots
    selected_key = None
    selected_slot = None
    for offset in range(4):
        slot_idx = (preferred_slot + offset) % 4
        key = groq_keys[slot_idx]
        if key:
            selected_key = key
            selected_slot = slot_idx + 1
            break

    if not selected_key:
        raise RuntimeError(
            "No active API keys found. Please set GEMINI_API_KEY, GOOGLE_API_KEY, "
            "or at least one of GROQ_API_KEY_1..4 / GROQ_API_KEY in your environment."
        )

    cache_key = ("groq", selected_slot, selected_key)
    if cache_key not in _llm_cache:
        model_name = settings.MODEL
        if "gemini" in model_name.lower():
            # Default fallback model for Groq if model setting is currently a Gemini one
            model_name = "llama-3.3-70b-versatile"
        print(f"[llm] Initializing Groq LLM for {agent_name} using Slot {selected_slot} and model {model_name}")
        _llm_cache[cache_key] = ChatGroq(
            model=model_name,
            groq_api_key=selected_key,
            temperature=0.6
        )

    return _llm_cache[cache_key]

# Backward compatibility singleton shim
try:
    llm = get_llm("default")
except Exception:
    # If no keys are set at start, don't fail import immediately
    llm = None