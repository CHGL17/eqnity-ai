import reapy
from typing import List
from langchain.tools import tool
from core.utils import _find_track, _find_fx
from core.models import ParameterChange

@tool
def list_tracks_and_vsts() -> str:
    """
    Lista todas las pistas del proyecto de Reaper y los VSTs que contienen.
    """
    try:
        project = reapy.Project()
        track_info = [
            f"Pista: '{track.name}' | VSTs: {', '.join([f"'{fx.name}' (clean: '{fx.name.split(': ')[-1]}')" for fx in track.fxs])}"
            for track in project.tracks if track.fxs
        ]
        return "\n".join(track_info) if track_info else "No se encontraron pistas con plugins VST."
    except Exception as e:
        return f"Error al conectar con Reaper: {e}."

@tool
def add_vst_to_track(track_name: str, vst_name: str) -> str:
    """
    Añade un nuevo plugin VST a una pista específica.
    """
    try:
        project = reapy.Project()
        track, error = _find_track(project, track_name)
        if error or track is None:
            return error or f"Error: No se encontró la pista '{track_name}'."
        try:
            new_fx = track.add_fx(vst_name)
            if new_fx and hasattr(new_fx, "name"):
                return f"Éxito: Se añadió '{new_fx.name}' a la pista '{track.name}'."
            return f"Error: No se pudo añadir el VST '{vst_name}'. ¿El nombre es correcto y está disponible en Reaper?"
        except AttributeError:
            return f"Error: La pista no soporta la operación 'add_fx'."
    except Exception as e:
        return f"Error inesperado al añadir VST: {e}"

@tool
def remove_vst_from_track(track_name: str, vst_name: str) -> str:
    """
    Elimina un plugin VST de una pista específica.
    """
    try:
        project = reapy.Project()
        track, error = _find_track(project, track_name)
        if error or track is None:
            return error or f"Error: No se encontró la pista '{track_name}'."
        fx_to_remove, error = _find_fx(track, vst_name)
        if error or fx_to_remove is None:
            return error or f"Error: No se pudo encontrar el VST '{vst_name}' en la pista especificada."
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
        if error or track is None:
            return error or f"Error: No se encontró la pista '{track_name}'."
        fx, error = _find_fx(track, vst_name)
        if error or fx is None:
            return error or f"Error: No se encontró el VST '{vst_name}' en la pista especificada."
        params_list = [f"'{p.name}' (Valor Actual: {p.formatted})" for p in fx.params]
        return f"Parámetros para '{fx.name}' en '{track.name}':\n" + ", ".join(params_list)
    except Exception as e:
        return f"Error inesperado al listar parámetros: {e}"

@tool
def set_multiple_vst_parameters(track_name: str, vst_name: str, changes: List[ParameterChange]) -> str:
    """
    Ajusta MÚLTIPLES parámetros de un VST en una sola llamada.
    """
    try:
        project = reapy.Project()
        track, error = _find_track(project, track_name)
        if error or not track:
            return error or f"Error: No se encontró la pista '{track_name}'."
        fx, error = _find_fx(track, vst_name)
        if error or not fx:
            return error or f"Error: No se encontró el VST '{vst_name}' en la pista '{track.name}'."
        results = []
        for change in changes:
            for i, p in enumerate(fx.params):
                if p.name.lower() == change.parameter_name.lower():
                    if 0.0 <= change.value <= 1.0:
                        fx.params[i] = change.value
                        results.append(f"  - '{p.name}' ajustado a {change.value:.2f}.")
                    else:
                        results.append(f"  - ERROR: Valor para '{p.name}' fuera de rango (0-1): {change.value}.")
                    break
            else:
                results.append(f"  - ERROR: Parámetro '{change.parameter_name}' no encontrado.")
        return f"Resultados de los ajustes en '{fx.name}':\n" + "\n".join(results)
    except Exception as e:
        return f"Error inesperado al ajustar múltiples parámetros: {e}"