from functools import lru_cache
from langchain_google_genai import ChatGoogleGenerativeAI
from app.config.settings import settings


@lru_cache(maxsize=1)
def get_chat_model() -> ChatGoogleGenerativeAI:
    if not settings.gemini_api_key:
        raise ValueError("GEMINI_API_KEY is not configured")
    return ChatGoogleGenerativeAI(
        model=settings.chat_model,
        google_api_key=settings.gemini_api_key,
        temperature=0.1,
    )
