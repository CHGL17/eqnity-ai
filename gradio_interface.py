import gradio as gr
import reapy
import uuid
from datetime import datetime
from typing import Dict, List, Tuple
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from agent.main import agent_executor

class ToneCraftInterface:
    def __init__(self):
        self.sessions: Dict[str, Dict] = {}
        self.current_session_id = None
        
    def create_new_session(self) -> str:
        """Crea una nueva sesión de conversación"""
        session_id = str(uuid.uuid4())[:8]
        session_name = f"Sesión {datetime.now().strftime('%H:%M:%S')}"
        
        self.sessions[session_id] = {
            "name": session_name,
            "thread_id": str(uuid.uuid4()),
            "created_at": datetime.now(),
            "messages": []
        }
        
        return session_id
    
    def get_session_names(self) -> List[Tuple[str, str]]:
        """Retorna lista de sesiones para el dropdown"""
        return [(session["name"], session_id) for session_id, session in self.sessions.items()]
    
    def load_chat_history(self, session_id: str) -> List[Tuple[str, str]]:
        """Carga el historial de chat de una sesión"""
        if session_id in self.sessions:
            return self.sessions[session_id]["messages"]
        return []
    
    def save_message(self, session_id: str, user_msg: str, bot_msg: str):
        """Guarda un mensaje en la sesión"""
        if session_id in self.sessions:
            self.sessions[session_id]["messages"].append((user_msg, bot_msg))
    
    def delete_session(self, session_id: str) -> List[Tuple[str, str]]:
        """Elimina una sesión"""
        if session_id in self.sessions:
            del self.sessions[session_id]
        return self.get_session_names()
    
    def clear_current_chat(self, session_id: str) -> List[Tuple[str, str]]:
        """Limpia el chat de la sesión actual"""
        if session_id in self.sessions:
            self.sessions[session_id]["messages"] = []
        return []

# Instancia global de la interfaz
interface = ToneCraftInterface()

def check_reaper_connection() -> Tuple[str, str]:
    """Verifica la conexión con Reaper"""
    try:
        reapy.Project()
        return "✅ Reaper conectado correctamente", "success"
    except Exception as e:
        return f"❌ Error de conexión: {str(e)}", "error"

def process_user_message(message: str, session_id: str, history: List[Tuple[str, str]]) -> Tuple[List[Tuple[str, str]], str]:
    """Procesa el mensaje del usuario y obtiene respuesta del agente"""
    if not session_id or session_id not in interface.sessions:
        return history, "❌ Error: No hay sesión activa. Crea una nueva sesión."
    
    if not message.strip():
        return history, ""
    
    try:
        # Configuración de la sesión
        thread_id = interface.sessions[session_id]["thread_id"]
        config = RunnableConfig(
            configurable={"thread_id": thread_id}, 
            run_id=uuid.uuid4()
        )
        
        # Procesar mensaje con el agente
        input_message = HumanMessage(content=message)
        bot_response = ""
        
        for event in agent_executor.stream(
            {"messages": [input_message]}, 
            config,
            stream_mode="values"
        ):
            if event["messages"] and event["messages"][-1].type == "ai":
                bot_response = event["messages"][-1].content
        
        # Actualizar historial
        new_history = history + [(message, bot_response)]
        
        # Guardar en la sesión
        interface.save_message(session_id, message, bot_response)
        
        return new_history, ""
        
    except Exception as e:
        error_msg = f"❌ Error procesando mensaje: {str(e)}"
        new_history = history + [(message, error_msg)]
        interface.save_message(session_id, message, error_msg)
        return new_history, ""

def create_new_session() -> Tuple[gr.update, gr.update, List[Tuple[str, str]]]:
    """Crea una nueva sesión y actualiza la interfaz"""
    session_id = interface.create_new_session()
    session_choices = interface.get_session_names()
    
    return (
        gr.update(choices=session_choices, value=session_id),  # Actualizar dropdown
        gr.update(value=session_id),  # Actualizar session_state
        []  # Limpiar chatbot
    )

def load_session(session_id: str) -> Tuple[List[Tuple[str, str]], str]:
    """Carga una sesión existente"""
    if session_id:
        history = interface.load_chat_history(session_id)
        return history, session_id
    return [], ""

def delete_current_session(session_id: str) -> Tuple[gr.update, gr.update, List[Tuple[str, str]]]:
    """Elimina la sesión actual"""
    if session_id:
        interface.delete_session(session_id)
    
    session_choices = interface.get_session_names()
    
    return (
        gr.update(choices=session_choices, value=None),  # Actualizar dropdown
        gr.update(value=""),  # Limpiar session_state
        []  # Limpiar chatbot
    )

def clear_chat(session_id: str) -> List[Tuple[str, str]]:
    """Limpia el chat de la sesión actual"""
    return interface.clear_current_chat(session_id)

# Crear la interfaz Gradio
def create_interface():
    with gr.Blocks(title="ToneCraft AI - Asistente de Mezcla", theme=gr.themes.Soft()) as app:
        gr.Markdown("""
        # 🎵 ToneCraft AI - Asistente Inteligente de Mezcla
        ### Controla Reaper con inteligencia artificial para mejorar tus mezclas
        """)
        
        # Estado de la sesión
        session_state = gr.State("")
        
        with gr.Row():
            with gr.Column(scale=3):
                # Panel de control de sesiones
                with gr.Group():
                    gr.Markdown("### 🎛️ Gestión de Sesiones")
                    
                    with gr.Row():
                        session_dropdown = gr.Dropdown(
                            choices=[],
                            label="Sesión Activa",
                            placeholder="Selecciona o crea una sesión",
                            scale=3
                        )
                        new_session_btn = gr.Button("➕ Nueva", scale=1, variant="primary")
                    
                    with gr.Row():
                        delete_session_btn = gr.Button("🗑️ Eliminar Sesión", variant="stop")
                        clear_chat_btn = gr.Button("🧹 Limpiar Chat", variant="secondary")
                
                # Chat principal
                chatbot = gr.Chatbot(
                    label="Conversación con ToneCraft",
                    height=400,
                    placeholder="Selecciona una sesión para comenzar...",
                    show_copy_button=True
                )
                
                with gr.Row():
                    msg_input = gr.Textbox(
                        label="Tu mensaje",
                        placeholder="Ej: 'Analiza la pista de guitarra y mejora su sonido'",
                        scale=4
                    )
                    send_btn = gr.Button("🚀 Enviar", scale=1, variant="primary")
            
            with gr.Column(scale=1):
                # Panel de estado
                with gr.Group():
                    gr.Markdown("### 📊 Estado del Sistema")
                    
                    connection_status = gr.HTML(value="🔄 Verificando conexión...")
                    refresh_btn = gr.Button("🔄 Verificar Conexión", variant="secondary")
                    
                    gr.Markdown("### 💡 Comandos Útiles")
                    gr.Markdown("""
                    - **"Lista las pistas"** - Ver todas las pistas y VSTs
                    - **"Analiza [pista]"** - Análisis de audio automático  
                    - **"Ecualiza [pista]"** - EQ automático
                    - **"Añade reverb a [pista]"** - Añadir efectos
                    - **"Parámetros de [VST]"** - Ver controles disponibles
                    """)
                    
                    gr.Markdown("### 🎯 Sesiones")
                    gr.Markdown("""
                    - Cada sesión mantiene su propia memoria
                    - Puedes alternar entre múltiples proyectos
                    - El historial se conserva automáticamente
                    """)
        
        # Event handlers
        def update_connection_status():
            status, status_type = check_reaper_connection()
            color = "#28a745" if status_type == "success" else "#dc3545"
            return f'<div style="color: {color}; font-weight: bold;">{status}</div>'
        
        # Cargar estado inicial
        app.load(
            fn=update_connection_status,
            outputs=connection_status
        )
        
        # Crear nueva sesión
        new_session_btn.click(
            fn=create_new_session,
            outputs=[session_dropdown, session_state, chatbot]
        )
        
        # Cargar sesión existente
        session_dropdown.change(
            fn=load_session,
            inputs=session_dropdown,
            outputs=[chatbot, session_state]
        )
        
        # Enviar mensaje
        def submit_message(message, session_id, history):
            return process_user_message(message, session_id, history)
        
        send_btn.click(
            fn=submit_message,
            inputs=[msg_input, session_state, chatbot],
            outputs=[chatbot, msg_input]
        )
        
        msg_input.submit(
            fn=submit_message,
            inputs=[msg_input, session_state, chatbot],
            outputs=[chatbot, msg_input]
        )
        
        # Eliminar sesión
        delete_session_btn.click(
            fn=delete_current_session,
            inputs=session_state,
            outputs=[session_dropdown, session_state, chatbot]
        )
        
        # Limpiar chat
        clear_chat_btn.click(
            fn=clear_chat,
            inputs=session_state,
            outputs=chatbot
        )
        
        # Verificar conexión
        refresh_btn.click(
            fn=update_connection_status,
            outputs=connection_status
        )
    
    return app

def main():
    """Función principal para ejecutar la interfaz"""
    print("🎵 Iniciando ToneCraft AI - Interfaz Gradio...")
    
    # Crear sesión inicial
    interface.create_new_session()
    
    app = create_interface()
    
    print("✅ Interfaz creada exitosamente")
    print("🌐 Abriendo en: http://localhost:7860")
    
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        inbrowser=True,
        show_error=True
    )

if __name__ == "__main__":
    main()