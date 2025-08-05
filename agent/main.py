from langchain_openai import ChatOpenAI
from pydantic import SecretStr
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from config import OPENROUTER_API_KEY
from agent.prompt import get_prompt_template
from tools.vst_tools import (
    list_tracks_and_vsts, list_vst_parameters, set_multiple_vst_parameters,
    add_vst_to_track, remove_vst_from_track
)
from tools.audio_tools import analyze_track_audio
from tools.ml_tools import analyze_uploaded_audio, suggest_audio_processing
from i18n.utils import i18n

# --- 1. Configuración de herramientas ---
tools = [
    list_tracks_and_vsts,
    list_vst_parameters,
    set_multiple_vst_parameters,
    add_vst_to_track,
    remove_vst_from_track,
    analyze_track_audio,
    analyze_uploaded_audio,
    suggest_audio_processing,
    # separate_audio_full
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

# --- 4. Función para crear/actualizar el agente con el idioma correcto ---
def create_agent_with_language(language: str = "es"):
    """Crea o actualiza el agente con el prompt en el idioma especificado"""
    if language is None:
        language = i18n.current_lang
    
    prompt_template = get_prompt_template(language)
    
    return create_react_agent(
        llm,
        tools,
        checkpointer=memory,
        prompt=prompt_template  # LangGraph usa state_schema en lugar de prompt
    )

# --- 5. Crear agente inicial ---
agent_executor = create_agent_with_language()

# --- 6. Función para actualizar el idioma del agente ---
def update_agent_language(language: str):
    """Actualiza el idioma del agente"""
    global agent_executor
    agent_executor = create_agent_with_language(language)