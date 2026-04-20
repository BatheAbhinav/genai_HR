from functools import lru_cache
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.config.settings import settings
import requests

# @lru_cache(maxsize=1)
# def get_embedding_client() -> GoogleGenerativeAIEmbeddings:
#     if not settings.gemini_api_key:
#         raise ValueError("GEMINI_API_KEY is not configured")
#     return GoogleGenerativeAIEmbeddings(
#         model=settings.embedding_model,
#         google_api_key=settings.gemini_api_key,
#     )


class GeminiEmbeddingClient:
    # We added 'dimensions' here so the class knows what to do with it
    def __init__(self, api_key: str, model: str, dimensions: int = 768):
        self.api_key = api_key
        self.model = model
        self.dimensions = dimensions
        # 2026 Standard: Use v1beta for gemini-embedding models
        self.url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:embedContent"

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        vectors = []
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key
        }

        for text in texts:
            response = requests.post(
                self.url,
                headers=headers,
                json={
                    "content": {
                        "parts": [{"text": text}]
                    }
                },
            )

            if response.status_code != 200:
                raise RuntimeError(f"Embedding failed ({response.status_code}): {response.text}")

            full_vector = response.json()["embedding"]["values"]
            
            # This line handles the 'trimming' to match your 768-dim DB
            truncated_vector = full_vector[:self.dimensions]
            vectors.append(truncated_vector)

        return vectors
    
    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]


@lru_cache(maxsize=1)
def get_embedding_client() -> GeminiEmbeddingClient:
    if not settings.gemini_api_key:
        raise ValueError("GEMINI_API_KEY is not configured")

    # Now this call matches the __init__ above
    return GeminiEmbeddingClient(
        api_key=settings.gemini_api_key,
        model="gemini-embedding-001",
        dimensions=768 
    )