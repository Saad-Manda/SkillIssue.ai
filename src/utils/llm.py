from llama_index.llms.google_genai import GoogleGenAI
from ..config import settings
from dotenv import load_dotenv
load_dotenv()

model_name = settings.MODEL
llm = GoogleGenAI(model = model_name, temperature=0.6)