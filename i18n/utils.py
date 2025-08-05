"""
Utilidades para el sistema de internacionalización
"""
import gradio as gr
from typing import Dict, Any
from .translations import get_translation, get_all_translations

# Estado global del idioma
current_language = gr.State("es")

class I18nManager:
    def __init__(self):
        self.current_lang = "es"
    
    def set_language(self, lang: str):
        """Establece el idioma actual"""
        if lang in ["es", "en"]:
            self.current_lang = lang
    
    def get(self, key: str) -> str:
        """Obtiene una traducción para el idioma actual"""
        return get_translation(key, self.current_lang)
    
    def get_all(self) -> Dict[str, Any]:
        """Obtiene todas las traducciones para el idioma actual"""
        return get_all_translations(self.current_lang)

# Instancia global del manager
i18n = I18nManager()

def t(key: str) -> str:
    """Función de conveniencia para obtener traducciones"""
    return i18n.get(key)

def update_language(lang: str):
    """Actualiza el idioma y retorna las nuevas traducciones"""
    i18n.set_language(lang)
    return i18n.get_all()