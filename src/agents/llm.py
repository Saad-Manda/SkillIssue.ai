from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from ..config import settings
from dotenv import load_dotenv
load_dotenv()

model_name = settings.MODEL
# llm = ChatGoogleGenerativeAI(model = model_name, temperature=0.6)
llm = ChatGroq(model=model_name, temperature=0.6)