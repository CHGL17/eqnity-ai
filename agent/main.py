from langchain_openai import ChatOpenAI
from pydantic import SecretStr
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from config import OPENROUTER_API_KEY
from agent.prompt import prompt_template
from tools.vst_tools import (
    list_tracks_and_vsts, list_vst_parameters, set_multiple_vst_parameters,
    add_vst_to_track, remove_vst_from_track
)
from tools.audio_tools import analyze_track_audio

# --- 1. Configuración de herramientas ---
tools = [
    list_tracks_and_vsts,
    list_vst_parameters,
    set_multiple_vst_parameters,
    add_vst_to_track,
    remove_vst_from_track,
    analyze_track_audio
]

# --- 2. Configuración del modelo ---
llm = ChatOpenAI(
    model="deepseek/deepseek-chat-v3-0324:free",
    temperature=0.1,
    api_key=SecretStr(OPENROUTER_API_KEY or ""),
    base_url="https://openrouter.ai/api/v1",
)

# --- 3. Configuración de memoria con LangGraph ---
memory = MemorySaver()

# --- 4. Crear agente con LangGraph ---
agent_executor = create_react_agent(
    llm,
    tools,
    checkpointer=memory,
    prompt=prompt_template
)