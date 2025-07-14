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
