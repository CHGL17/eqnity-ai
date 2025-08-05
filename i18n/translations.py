"""
Sistema de internacionalización para EQnity AI
"""

translations = {
    "es": {
        # UI General
        "app_title": "EQnity AI",
        "app_subtitle": "Tu asistente inteligente para producción musical en Reaper",
        "conversation": "Conversación",
        "send": "Enviar",
        "clear_conversation": "🗑️ Borrar Conversación",
        "language": "Idioma",
        "processing_request": "🤔 Procesando tu solicitud...",
        "analysis_completed": "✅ Análisis completado",
        "error_occurred": "❌ Ha ocurrido un error",
        
        # Placeholders y ejemplos
        "input_placeholder": "Ej: 'Analiza la pista de bajo y mejora su claridad'",
        "welcome_message": "¡Hola! Soy EQnity AI. Puedo ayudarte a analizar y mejorar tus pistas de audio en Reaper. ¿Qué necesitas?",
        "conversation_restarted": "¡Hola! Soy EQnity AI. La conversación ha sido reiniciada. ¿En qué puedo ayudarte?",
        
        # ML Analysis Section
        "ml_analysis": "🤖 Análisis con ML",
        "audio_track": "Pista de Audio",
        "analyze": "🔍 Analizar",
        "suggest_processing": "💡 Sugerir procesamiento",
        "separate_instruments": "🎵 Separar instrumentos",
        "upload_audio_first": "Por favor, sube un archivo de audio primero.",
        
        # Examples
        "examples_title": "💬 Ejemplos",
        "example_1": "La pista de bajo suena muy embarrada, analízala y arréglala",
        "example_2": "Normaliza el volumen de todas las pistas y aplica un limitador suave al master",
        "example_3": "Analiza el espectro de frecuencias de la pista 'Vocals' y sugiere mejoras",
        
        # Quick Commands
        "quick_commands": "📋 Comandos Rápidos",
        "analysis_cmd": "**Análisis:** \"Analiza la pista X\"",
        "processing_cmd": "**Procesamiento:** \"Normaliza el volumen\"",
        "export_cmd": "**Exportación:** \"Exporta la pista\"",
        
        # Tips
        "tips": "💡 Tips",
        "tip_specific": "- Sé específico con los nombres de pista.",
        "tip_thinking": "- El agente mostrará su proceso de pensamiento antes de la respuesta final.",
        
        # Tool calls
        "tool_call": "🔧 Llamada a herramienta",
        "tool_result": "✅ Resultado de herramienta",
        
        # File analysis
        "analyze_audio": "Analiza el audio",
        "suggest_processing_for": "Sugiere procesamiento para",
        "separate_instruments_from": "Separa instrumentos de",
    },
    
    "en": {
        # UI General
        "app_title": "EQnity AI",
        "app_subtitle": "Your intelligent assistant for music production in Reaper",
        "conversation": "Conversation",
        "send": "Send",
        "clear_conversation": "🗑️ Clear Conversation",
        "language": "Language",
        "processing_request": "🤔 Processing your request...",
        "analysis_completed": "✅ Analysis completed",
        "error_occurred": "❌ An error occurred",
        
        # Placeholders y ejemplos
        "input_placeholder": "e.g., 'Analyze the bass track and improve its clarity'",
        "welcome_message": "Hello! I'm EQnity AI. I can help you analyze and improve your audio tracks in Reaper. What do you need?",
        "conversation_restarted": "Hello! I'm EQnity AI. The conversation has been restarted. How can I help you?",
        
        # ML Analysis Section
        "ml_analysis": "🤖 ML Analysis",
        "audio_track": "Audio Track",
        "analyze": "🔍 Analyze",
        "suggest_processing": "💡 Suggest processing",
        "separate_instruments": "🎵 Separate instruments",
        "upload_audio_first": "Please upload an audio file first.",
        
        # Examples
        "examples_title": "💬 Examples",
        "example_1": "The bass track sounds muddy, analyze it and fix it",
        "example_2": "Normalize the volume of all tracks and apply a soft limiter to the master",
        "example_3": "Analyze the frequency spectrum of the 'Vocals' track and suggest improvements",
        
        # Quick Commands
        "quick_commands": "📋 Quick Commands",
        "analysis_cmd": "**Analysis:** \"Analyze track X\"",
        "processing_cmd": "**Processing:** \"Normalize volume\"",
        "export_cmd": "**Export:** \"Export track\"",
        
        # Tips
        "tips": "💡 Tips",
        "tip_specific": "- Be specific with track names.",
        "tip_thinking": "- The agent will show its thinking process before the final response.",
        
        # Tool calls
        "tool_call": "🔧 Tool call",
        "tool_result": "✅ Tool result",
        
        # File analysis
        "analyze_audio": "Analyze audio",
        "suggest_processing_for": "Suggest processing for",
        "separate_instruments_from": "Separate instruments from",
    }
}

def get_translation(key: str, lang: str = "es") -> str:
    """
    Obtiene una traducción para una clave dada en el idioma especificado.
    """
    return translations.get(lang, {}).get(key, translations["es"].get(key, key))

def get_all_translations(lang: str = "es") -> dict:
    """
    Obtiene todas las traducciones para un idioma específico.
    """
    return translations.get(lang, translations["es"])