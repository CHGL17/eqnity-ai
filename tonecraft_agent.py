import os
import reapy
import time
import numpy as np
import librosa
import soundfile as sf
import pyloudnorm as pyln
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

# --- 2. FUNCIONES AUXILIARES Y MODELOS DE DATOS (Tu código, intacto y respetado) ---
def _find_track(project, track_name):
    for track in project.tracks:
        if track.name.lower() == track_name.lower():
            return track, None
    return None, f"Error: No se encontró la pista '{track_name}'."

def _find_fx(track, vst_name):
    for fx in track.fxs:
        clean_fx_name = fx.name.split(': ')[-1]
        if (fx.name.lower() == vst_name.lower() or 
            clean_fx_name.lower() == vst_name.lower()):
            return fx, None
    return None, f"Error: No se encontró el VST '{vst_name}' en la pista '{track.name}'."

class ParameterChange(BaseModel):
    parameter_name: str = Field(description="El nombre exacto del parámetro a cambiar.")
    value: float = Field(description="El nuevo valor normalizado para el parámetro, entre 0.0 y 1.0.")

# --- 3. HERRAMIENTAS (Tus herramientas + las nuevas integradas) ---

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
                vst_names = [f"'{fx.name}' (clean: '{fx.name.split(': ')[-1]}')" for fx in track.fxs]
                track_info.append(f"Pista: '{track.name}' | VSTs: {', '.join(vst_names)}")
        if not track_info: return "No se encontraron pistas con plugins VST."
        return "\n".join(track_info)
    except Exception as e:
        return f"Error al conectar con Reaper: {e}."

@tool
def add_vst_to_track(track_name: str, vst_name: str) -> str:
    """
    (NUEVA) Añade un nuevo plugin VST a una pista específica. El nombre del VST debe ser exacto
    a como aparece en la lista de FX de Reaper. Útil para añadir un EQ o compresor cuando se necesita.
    """
    try:
        project = reapy.Project()
        track, error = _find_track(project, track_name)
        if error or track is None:
            return error or f"Error: No se encontró la pista '{track_name}'."
        
        try:
            new_fx = track.add_fx(vst_name)
        except AttributeError:
            return f"Error: La pista no soporta la operación 'add_fx'."
        if new_fx is None or not hasattr(new_fx, "name"):
            return f"Error: No se pudo añadir el VST '{vst_name}'. ¿El nombre es correcto y está disponible en Reaper?"
        
        return f"Éxito: Se añadió '{new_fx.name}' a la pista '{track.name}'."
    except Exception as e:
        return f"Error inesperado al añadir VST: {e}"

@tool
def remove_vst_from_track(track_name: str, vst_name: str) -> str:
    """
    (NUEVA) Elimina un plugin VST de una pista específica.
    """
    try:
        project = reapy.Project()
        track, error = _find_track(project, track_name)
        if error: return error
        
        fx_to_remove, error = _find_fx(track, vst_name)
        if error or fx_to_remove is None:
            return error or f"Error: No se pudo encontrar el VST '{vst_name}' en la pista '{track.name}' para eliminarlo."
        
        fx_to_remove.delete()
        return f"Éxito: Se eliminó el VST de la pista '{track.name}'."
    except Exception as e:
        return f"Error inesperado al eliminar VST: {e}"

@tool
def list_vst_parameters(track_name: str, vst_name: str) -> str:
    """
    Lista los parámetros de un VST, incluyendo su valor actual formateado.
    """
    try:
        project = reapy.Project()
        track, error = _find_track(project, track_name)
        if error: return error
        
        fx, error = _find_fx(track, vst_name)
        if error: return error

        params_list = [f"'{p.name}' (Valor Actual: {p.formatted})" for p in fx.params]
        return f"Parámetros para '{fx.name}' en '{track.name}':\n" + ", ".join(params_list)
    except Exception as e:
        return f"Error inesperado al listar parámetros: {e}"
        
@tool
def set_multiple_vst_parameters(track_name: str, vst_name: str, changes: List[ParameterChange]) -> str:
    """
    Ajusta MÚLTIPLES parámetros de un VST en una sola llamada. Ideal para aplicar un preset o un cambio complejo.
    """
    try:
        project = reapy.Project()
        track, error = _find_track(project, track_name)
        if error: return error
        
        fx, error = _find_fx(track, vst_name)
        if error: return error

        results = []
        for change in changes:
            # Reutilizando tu lógica de búsqueda y asignación segura
            param_found = False
            for i, p in enumerate(fx.params):
                if p.name.lower() == change.parameter_name.lower():
                    if 0.0 <= change.value <= 1.0:
                        fx.params[i] = change.value
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
def analyze_track_audio(track_name: str, duration: int = 10) -> str:
    """
    Renderiza un clip de la pista usando el contexto de Reaper.
    """
    import tempfile
    import time
    original_mutes = {}
    project = reapy.Project()
    temp_dir = os.path.join(project.path, "temp_audio")
    os.makedirs(temp_dir, exist_ok=True)
    temp_file = tempfile.mktemp(suffix=".wav", dir=temp_dir)
    
    try:
        track, error = _find_track(project, track_name)
        if error: return error

        # Usar el contexto de Reaper para operaciones seguras
        with project.make_current_project():
            # Mutea todas las pistas menos la deseada
            for t in project.tracks:
                original_mutes[t.id] = t.is_muted
                if t.id != track.id:
                    t.mute()
            track.unmute()

            # Guardar configuración de render previa
            prev_render_file = project.get_info_string("RENDER_FILE")
            prev_render_pattern = project.get_info_string("RENDER_PATTERN")
            prev_render_boundsflag = project.get_info_value("RENDER_BOUNDSFLAG")
            prev_render_start = project.get_info_value("RENDER_STARTPOS")
            prev_render_end = project.get_info_value("RENDER_ENDPOS")
            prev_render_settings = project.get_info_value("RENDER_SETTINGS")

            # Configurar render temporal
            project.set_info_string("RENDER_FILE", temp_file)
            project.set_info_string("RENDER_PATTERN", "")
            project.set_info_value("RENDER_BOUNDSFLAG", 0)
            start_time = project.cursor_position
            end_time = start_time + duration
            project.set_info_value("RENDER_STARTPOS", start_time)
            project.set_info_value("RENDER_ENDPOS", end_time)
            project.set_info_value("RENDER_SETTINGS", 2)

            # Seleccionar solo la pista deseada
            for t in project.tracks:
                t.unselect()
            track.select()

            # Ejecutar acción de render
            # project.perform_action(42230)
            project.perform_action(41824)
            project.perform_action(40078)  # Acción: "Refresh all windows" para forzar actualización

            # Esperar con timeout extendido
            prev_size = -1
            for i in range(300):  # Hasta 30 segundos
                print(temp_file, f" - Esperando renderizado... ({i+1}/300)", os.path.exists(temp_file + '\\test-ai.wav'), os.path.getsize(temp_file + '\\test-ai.wav'), temp_file + '\\test-ai.wav')
                if os.path.exists(temp_file):
                    try:
                        current_size = os.path.getsize(temp_file + '\\test-ai.wav')
                        if current_size == prev_size and current_size > 0:
                            with open(temp_file + '\\test-ai.wav', "rb") as f:
                                f.read(1)
                            time.sleep(0.5)
                            break
                        prev_size = current_size
                    except PermissionError as e:
                        print(f"Error de permiso al acceder al archivo: {e}. Esperando...")
                        pass
                time.sleep(0.1)
            else:
                return "Error: Timeout en renderizado o archivo bloqueado."

            # Restaurar configuración inmediatamente
            project.set_info_string("RENDER_FILE", prev_render_file)
            project.set_info_string("RENDER_PATTERN", prev_render_pattern)
            project.set_info_value("RENDER_BOUNDSFLAG", prev_render_boundsflag)
            project.set_info_value("RENDER_STARTPOS", prev_render_start)
            project.set_info_value("RENDER_ENDPOS", prev_render_end)
            project.set_info_value("RENDER_SETTINGS", prev_render_settings)

        # Análisis del archivo (fuera del contexto de Reaper)
        time.sleep(2)  # Retraso adicional antes de leer
        audio, sr = sf.read(temp_file + '\\test-ai.wav')
        if audio.ndim > 1: 
            audio = audio.mean(axis=1)
        
        meter = pyln.Meter(sr)
        loudness = meter.integrated_loudness(audio)
        spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=audio, sr=sr))
        
        report = f"Reporte de Análisis de Audio para '{track_name}':\n"
        report += f"- Loudness: {loudness:.2f} LUFS.\n"
        if spectral_centroid < 1000: 
            report += "- Carácter Sónico: Oscuro/Grave.\n"
        elif 1000 <= spectral_centroid < 2500: 
            report += "- Carácter Sónico: Balanceado/Medioso.\n"
        else: 
            report += "- Carácter Sónico: Brillante/Agudo.\n"
            
        return report

    except Exception as e:
        return f"Error durante el análisis de audio: {e}"
    finally:
        # Restaurar mutes
        if 'project' in locals() and 'original_mutes' in locals():
            for t in project.tracks:
                if t.id in original_mutes:
                    if original_mutes[t.id]: 
                        t.mute()
                    else: 
                        t.unmute()
        # Limpiar archivo
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except:
                pass  # Si no se puede eliminar, no es crítico

# --- 4. CREACIÓN DEL AGENTE (CON PROMPT ACTUALIZADO) ---

tools = [
    list_tracks_and_vsts, 
    list_vst_parameters, 
    set_multiple_vst_parameters, 
    # Añadiendo las nuevas herramientas a la lista del agente
    add_vst_to_track,
    remove_vst_from_track,
    analyze_track_audio
]

llm = ChatOpenAI(
    model="deepseek/deepseek-chat-v3-0324:free",
    temperature=0.1,
    api_key=SecretStr(OPENROUTER_API_KEY),
    base_url="https://openrouter.ai/api/v1",
)

prompt_template = """
<role>
Eres "ToneCraft", un asistente de ingeniero de sonido experto que opera en Reaper. Eres proactivo, eficiente y ahora tienes la capacidad de "escuchar" y diagnosticar problemas de audio.
</role>

<instructions>
1.  **Diagnostica Antes de Actuar:** Si la petición del usuario es subjetiva (ej: "suena mal", "arréglalo", "hazlo sonar mejor", "está muy embarrado"), tu PRIMERA ACCIÓN debe ser usar la herramienta `analyze_track_audio`. Usa el reporte que genera para formar un plan de acción concreto.
2.  **Planifica y Ejecuta:** Basado en el diagnóstico del análisis (o en una petición directa del usuario), forma un plan. Si necesitas un efecto que no está (ej: un ecualizador para quitar 'mud'), usa `add_vst_to_track` para añadirlo. El ecualizador por defecto de Reaper es 'ReaEQ (Cockos)'.
3.  **Eficiencia Máxima:** Cuando necesites hacer varios ajustes en un solo VST (como configurar un EQ), agrupa todos los cambios en UNA SOLA llamada a `set_multiple_vst_parameters`.
4.  **Verifica Siempre:** Antes de ajustar un VST, si no estás 100% seguro de los nombres de los parámetros, usa `list_vst_parameters` para confirmarlos. La información del "Valor Actual" es crucial para decidir cuánto cambiar algo.
5.  **Usa la Memoria:** Revisa el `<chat_history>` para entender el contexto. Si el usuario dice "un poco más", refiérete al último ajuste que hiciste.
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
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
agent = create_openai_tools_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent, 
    tools=tools, 
    verbose=True, 
    memory=memory, 
    handle_parsing_errors="Por favor, revisa tu petición. No pude procesarla correctamente."
)

# --- 5. INTERFAZ DE CONSOLA ---
def main():
    print("--- Bienvenido a ToneCraft AI v2.1 (con Oído Digital y Gestión de FX) ---")
    print("Asegúrate de tener instaladas las librerías: librosa, numpy, soundfile, pyloudnorm")
    try:
        reapy.Project()
        print("¡Conexión con Reaper exitosa!")
    except Exception as e:
        print(f"Error fatal: No se pudo conectar con Reaper. ¿Está abierto y configurado?")
        return

    print("Escribe tu petición (o 'salir'). Ej: 'La pista de bajo suena muy embarrada, analízala y arréglala.'")
    
    while True:
        user_query = input("\nUsuario > ")
        if user_query.lower() in ["salir", "exit", "quit"]:
            break
        if user_query:
            try:
                result = agent_executor.invoke({"input": user_query})
                print(f"\nToneCraft > {result['output']}")
            except Exception as e:
                print(f"\nHa ocurrido un error inesperado en el agente: {e}")

if __name__ == "__main__":
    main()