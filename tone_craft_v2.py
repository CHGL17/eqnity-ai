import os
import reapy
from dotenv import load_dotenv
from typing import List

# --- Langchain & Pydantic Imports ---
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain.tools import tool
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import AIMessage, HumanMessage
from pydantic import BaseModel, Field, SecretStr

# --- 1. CONFIGURACIÓN INICIAL ---
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    print("Error: La variable de entorno OPENROUTER_API_KEY no está configurada.")
    exit()

# --- 2. FUNCIONES AUXILIARES Y MODELOS DE DATOS ---
def _find_track(project, track_name):
    for track in project.tracks:
        if track.name.lower() == track_name.lower():
            return track, None
    return None, f"Error: No se encontró la pista '{track_name}'."

def _find_fx(track, vst_name):
    for fx in track.fxs:
        # Comparar tanto el nombre completo como el nombre sin prefijos
        clean_fx_name = fx.name.split(': ')[-1]
        if (fx.name.lower() == vst_name.lower() or 
            clean_fx_name.lower() == vst_name.lower()):
            return fx, None
    return None, f"Error: No se encontró el VST '{vst_name}' en la pista '{track.name}'."

# Modelo Pydantic para la nueva herramienta de múltiples parámetros.
class ParameterChange(BaseModel):
    parameter_name: str = Field(description="El nombre exacto del parámetro a cambiar.")
    value: float = Field(description="El nuevo valor normalizado para el parámetro, entre 0.0 y 1.0.")

# --- 3. HERRAMIENTAS MEJORADAS ---

@tool
def list_tracks_and_vsts() -> str:
    """
    Lista todas las pistas del proyecto de Reaper y los VSTs que contienen.
    """
    try:
        project = reapy.Project()
        track_info = []
        for track in project.tracks:
            if track.fxs:
                vst_names = []
                for fx in track.fxs:
                    # Mostrar tanto el nombre completo como el limpio
                    clean_name = fx.name.split(': ')[-1]
                    vst_names.append(f"'{fx.name}' (clean: '{clean_name}')")
                track_info.append(f"Pista: '{track.name}' | VSTs: {vst_names}")
        
        if not track_info:
            return "No se encontraron pistas con plugins VST en el proyecto."
        return "\n".join(track_info)
    except Exception as e:
        return f"Error al conectar con Reaper: {e}."

@tool
def list_vst_parameters(track_name: str, vst_name: str) -> str:
    """
    Lista los parámetros de un VST, incluyendo su valor actual formateado para dar contexto.
    """
    try:
        project = reapy.Project()
        track, error = _find_track(project, track_name)
        if error: return error
        
        fx, error = _find_fx(track, vst_name)
        if error or fx is None or track is None:
            return error if error else "Error: No se pudo encontrar la pista o el VST."

        # Devolvemos el nombre y el valor actual formateado (ej: "800.0 Hz")
        params_list = [f"'{p.name}' (Valor Actual: {p.formatted})" for p in fx.params]
        return f"Parámetros para '{fx.name}' en '{track.name}':\n" + ", ".join(params_list)
    except Exception as e:
        return f"Error inesperado al listar parámetros: {e}"

@tool
def set_multiple_vst_parameters(track_name: str, vst_name: str, changes: List[ParameterChange]) -> str:
    """
    Ajusta MÚLTIPLES parámetros de un VST en una sola llamada. Ideal para aplicar un preset o un cambio complejo como una ecualización.
    """
    try:
        project = reapy.Project()
        track, error = _find_track(project, track_name)
        if error: return error
        
        fx, error = _find_fx(track, vst_name)
        if error or fx is None:
            return error if error else f"Error: No se encontró el VST '{vst_name}' en la pista '{track}'."

        results = []
        for change in changes:
            param_found = False
            for i, p in enumerate(fx.params):
                if p.name.lower() == change.parameter_name.lower():
                    if 0.0 <= change.value <= 1.0:
                        fx.params[i] = change.value  # Usar el índice para asignar
                        results.append(f"  - '{p.name}' ajustado a {change.value:.2f}.")
                        param_found = True
                    else:
                        results.append(f"  - ERROR: Valor para '{p.name}' fuera de rango (0-1): {change.value}.")
                    break
            if not param_found:
                results.append(f"  - ERROR: Parámetro '{change.parameter_name}' no encontrado.")

        return f"Resultados de los ajustes en '{fx.name}':\n" + "\n".join(results)
    except Exception as e:
        return f"Error inesperado al ajustar múltiples parámetros: {str(e)}"

@tool
def set_vst_parameter(track_name: str, vst_name: str, parameter_name: str, value: float) -> str:
    """
    Ajusta UN SOLO parámetro de un VST. Para múltiples cambios, usa set_multiple_vst_parameters.
    """
    try:
        project = reapy.Project()
        track, error = _find_track(project, track_name)
        if error: return error
        
        fx, error = _find_fx(track, vst_name)
        if error or fx is None:
            return error if error else f"Error: No se encontró el VST '{vst_name}' en la pista '{track}'."

        # Buscar el parámetro usando enumerate para obtener el índice
        for i, p in enumerate(fx.params):
            if p.name.lower() == parameter_name.lower():
                if 0.0 <= value <= 1.0:
                    fx.params[i] = value  # Usar el índice para asignar
                    return f"Éxito: '{p.name}' ajustado a {value:.2f} en '{fx.name}' (pista '{track}')."
                else:
                    return f"Error: El valor debe estar entre 0.0 y 1.0. Recibido: {value}"
        
        return f"Error: No se encontró el parámetro '{parameter_name}' en '{fx.name}'."
    except Exception as e:
        return f"Error al ajustar el parámetro: {str(e)}"

# --- 4. CREACIÓN DEL AGENTE CON MEMORIA Y PROMPT MEJORADO ---
tools = [list_tracks_and_vsts, list_vst_parameters, set_multiple_vst_parameters, set_vst_parameter]

llm = ChatOpenAI(
    model="deepseek/deepseek-chat-v3-0324:free",
    temperature=0.1,
    api_key=SecretStr(OPENROUTER_API_KEY),
    base_url="https://openrouter.ai/api/v1",
)

# Prompt mejorado para ser más proactivo y usar las nuevas herramientas.
prompt_template = """
<role>
Eres "ToneCraft", un asistente de ingeniero de sonido experto. Tu propósito es traducir las peticiones creativas de un usuario en ajustes concretos de plugins VST en Reaper. Eres proactivo, eficiente y seguro.
</role>

<instructions>
1.  **Sé Proactivo:** Si el usuario te da una tarea clara (ej: "ecualiza la guitarra para heavy metal"), formula un plan y EJECÚTALO directamente usando la herramienta `set_multiple_vst_parameters`. No pidas permiso si la intención es clara. Informa al usuario de lo que HAS HECHO.
2.  **Usa las Herramientas Correctamente:**
    *   `list_tracks_and_vsts`: Para obtener una vista general del proyecto.
    *   `list_vst_parameters`: Para ver los nombres exactos y los valores actuales de los parámetros. La información del valor actual es crucial para decidir cuánto cambiar un parámetro.
    *   `set_multiple_vst_parameters`: Tu herramienta principal para aplicar cambios. Agrupa todos los ajustes en una sola llamada a esta herramienta.
    *   `set_vst_parameter`: Solo para cambios individuales simples.
3.  **Manejo de Parámetros:**
    *   Recuerda que los valores que estableces deben estar normalizados entre 0.0 y 1.0.
    *   Para parámetros On/Off, 0.0 es 'Off' y 1.0 es 'On'.
    *   Para frecuencias (Hz) o ganancias (dB), usa el "Valor Actual" que te da `list_vst_parameters` como referencia para decidir el nuevo valor normalizado. Un pequeño cambio en el valor normalizado puede ser un gran cambio en Hz.
4.  **Memoria:** Usa el historial de la conversación para entender el contexto. Si el usuario dice "un poco más", refiérete al último ajuste que hiciste.
</instructions>

<chat_history>
{chat_history}
</chat_history>

<user_input>
{input}
</user_input>

<agent_scratchpad>
{agent_scratchpad}
</agent_scratchpad>
"""

prompt = ChatPromptTemplate.from_template(prompt_template)

# Configuración de la memoria
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

agent = create_openai_tools_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent, 
    tools=tools, 
    verbose=True, 
    memory=memory, 
    handle_parsing_errors=True
)

# --- 5. INTERFAZ DE CONSOLA CON MEMORIA ---
def main():
    print("--- Bienvenido a ToneCraft AI v2.0 (con Memoria y Superpoderes) ---")
    print("Conectando con Reaper...")
    
    try:
        reapy.Project()
        print("¡Conexión con Reaper exitosa!")
    except Exception as e:
        print(f"Error fatal: No se pudo conectar con Reaper. ¿Está abierto y configurado?")
        print(f"Detalle: {e}")
        return

    print("Escribe tu petición (o 'salir' para terminar). Ej: 'Ecualiza la guitarra para heavy metal'")
    
    while True:
        user_query = input("\nUsuario > ")
        if user_query.lower() in ["salir", "exit", "quit"]:
            print("¡Hasta pronto!")
            break
        
        if user_query:
            try:
                # El historial se pasa implícitamente por el objeto 'memory'
                result = agent_executor.invoke({"input": user_query})
                print(f"\nToneCraft > {result['output']}")
            except Exception as e:
                print(f"\nHa ocurrido un error inesperado en el agente: {e}")

if __name__ == "__main__":
    main()import os