from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=os.getenv("GEMINI_API_KEY")
)