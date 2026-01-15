from langchain_upstage import ChatUpstage
from config.settings import TEMPERATURE

def get_llm():
    return ChatUpstage(
        model="solar-1-mini-chat",
        temperature=TEMPERATURE,
    )