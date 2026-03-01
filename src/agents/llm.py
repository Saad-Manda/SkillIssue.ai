from langchain_google_genai import ChatGoogleGenerativeAI
from ..config import settings
from dotenv import load_dotenv
load_dotenv()

model_name = settings.MODEL
llm = ChatGoogleGenerativeAI(model = model_name, temperature=0.6)