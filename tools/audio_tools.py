import os
import tempfile
import time
import numpy as np
import soundfile as sf
import pyloudnorm as pyln
import librosa
import reapy
from langchain.tools import tool
from core.utils import _find_track

@tool
def analyze_track_audio(track_name: str, duration: int = 10) -> str:
    """
    Renderiza un clip de la pista usando el contexto de Reaper y analiza el audio resultante.
    """
    original_mutes = {}
    project = reapy.Project()
    temp_dir = os.path.join(project.path, "temp_audio")
    os.makedirs(temp_dir, exist_ok=True)
    temp_file = tempfile.mktemp(dir=temp_dir)
    file_name = f"\\{project.name.split('.')[0]}.wav"

    try:
        track, error = _find_track(project, track_name)
        if error or not track:
            return error or f"Error: No se encontró la pista '{track_name}'."

        with project.make_current_project():
            # Guardar estado de mute y mutear otras pistas
            for t in project.tracks:
                original_mutes[t.id] = t.is_muted
                if t.id != track.id:
                    t.mute()
            track.unmute()
    
            # Guardar y ajustar configuración de render
            prev_settings = {
                "RENDER_FILE": project.get_info_string("RENDER_FILE"),
                "RENDER_PATTERN": project.get_info_string("RENDER_PATTERN"),
                "RENDER_BOUNDSFLAG": project.get_info_value("RENDER_BOUNDSFLAG"),
                "RENDER_STARTPOS": project.get_info_value("RENDER_STARTPOS"),
                "RENDER_ENDPOS": project.get_info_value("RENDER_ENDPOS"),
                "RENDER_SETTINGS": project.get_info_value("RENDER_SETTINGS"),
            }
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
    
            # Renderizar (guardar como archivo)
            # Pon en primer plano reaper para evitar problemas de pistas offline
            project.perform_action(41824)
            project.perform_action(40078)  # Render to file
    
            # Esperar a que el archivo se genere
            for _ in range(300):
                print(temp_file, file_name, os.path.exists(temp_file), os.path.getsize(temp_file + file_name))
                if os.path.exists(temp_file) and os.path.getsize(temp_file + file_name) > 0:
                    with open(temp_file + file_name, "rb") as f:
                        f.read(1)
                    time.sleep(0.5)
                    break
                time.sleep(0.1)
            else:
                return "Error: Timeout esperando el renderizado."
    
            # Restaurar configuración de render
            for key, value in prev_settings.items():
                if isinstance(value, str):
                    project.set_info_string(key, value)
                else:
                    project.set_info_value(key, value)
    
            # Leer y analizar el audio
            time.sleep(2)  # Retraso adicional antes de leer
            audio, sr = sf.read(temp_file + file_name)
            if audio.ndim > 1:
                audio = np.mean(audio, axis=1)
                
            meter = pyln.Meter(sr)
            loudness = meter.integrated_loudness(audio)
            spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=audio, sr=sr))
    
            brillo = (
                "- El audio es oscuro/mate (bajo brillo).\n" if spectral_centroid < 1000 else
                "- El audio tiene un balance medio de brillo.\n" if spectral_centroid < 2500 else
                "- El audio es brillante/agudo.\n"
            )
            return (
                f"Reporte de Análisis de Audio para '{track_name}':\n"
                f"- Loudness: {loudness:.2f} LUFS.\n"
                f"{brillo}"
            )

    except Exception as e:
        return f"Error durante el análisis de audio: {e}"
    finally:
        # Restaurar estado de mute
        for t in project.tracks:
            if t.id in original_mutes:
                t.mute() if original_mutes[t.id] else t.unmute()
        # Eliminar archivo temporal
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except Exception:
                pass
