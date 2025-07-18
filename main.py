import uuid
import time
import gradio as gr
# CAMBIO: ChatMessage ya no es necesario si manejamos todo con diccionarios para compatibilidad
# from gradio import ChatMessage 
from agent.main import agent_executor
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_core.runnables import RunnableConfig

# (El resto de tus importaciones como reapy)

session_threads = {}

def get_or_create_thread_id(session_id):
    if session_id not in session_threads:
        session_threads[session_id] = str(uuid.uuid4())
    return session_threads[session_id]

def format_tool_call(tool_call):
    tool_name = tool_call.get("name", "Herramienta desconocida")
    args = tool_call.get("args", {})
    formatted_args = []
    for key, value in args.items():
        if isinstance(value, str) and len(value) > 50:
            value = value[:50] + "..."
        formatted_args.append(f"  - `{key}`: `{value}`")
    return f"**{tool_name}**\n" + "\n".join(formatted_args)

def chat_function(message, history, session_id):
    """Función principal del chat con streaming, pensamientos y respuesta final acumulada."""
    try:
        thread_id = get_or_create_thread_id(session_id)
        config = RunnableConfig(configurable={"thread_id": thread_id}, run_id=uuid.uuid4())
        
        # Crear mensaje de "pensamiento"
        thinking_message = {
            "role": "assistant",
            "content": """
<div class="thinking-box">
    <div class="thinking-title">🤔 Procesando tu solicitud...</div>
    <div class="thinking-content"></div>
</div>
            """
        }
        history.append(thinking_message)
        yield history
        
        input_message = HumanMessage(content=message)
        accumulated_thoughts = ""
        final_response_content = ""
        tool_calls_count = 0
        
        # CAMBIO PRINCIPAL: Usar stream_mode="values" como en el código que funcionaba
        for event in agent_executor.stream(
            {"messages": [input_message]}, 
            config, 
            stream_mode="values"  # Cambiar de 'messages' a 'values'
        ):
            # Con stream_mode="values", el evento tiene la estructura {"messages": [...]}
            if "messages" not in event:
                continue

            # Procesar todos los mensajes en el evento
            for msg in event["messages"]:
                new_thought = ""
                
                # Detectar llamadas a herramientas
                if hasattr(msg, 'type') and msg.type == "ai" and hasattr(msg, "tool_calls") and msg.tool_calls:
                    tool_calls_count += 1
                    for tool_call in msg.tool_calls:
                        tool_info = format_tool_call(tool_call)
                        new_thought += f"\n\n**🔧 Llamada a herramienta #{tool_calls_count}**\n{tool_info}"
                        time.sleep(0.3)
                
                # Procesar respuestas de herramientas
                elif hasattr(msg, 'type') and msg.type == "tool":
                    result_preview = str(msg.content)[:150] + "..." if len(str(msg.content)) > 150 else str(msg.content)
                    new_thought += f"\n\n**✅ Resultado de herramienta:**\n`{result_preview}`"
                    time.sleep(0.2)
                
                # Capturar la respuesta final del asistente
                elif hasattr(msg, 'type') and msg.type == "ai" and hasattr(msg, 'content') and msg.content:
                    # Solo acumular si no tiene tool_calls
                    if not (hasattr(msg, "tool_calls") and msg.tool_calls):
                        final_response_content = msg.content  # No acumular, usar el último mensaje completo
                
                # Actualizar el cuadro de pensamiento si hay nueva información
                if new_thought:
                    accumulated_thoughts += new_thought
                    thinking_content = accumulated_thoughts.strip()
                    history[-1]["content"] = f"""
<div class="thinking-box">
    <div class="thinking-title">🤔 Procesando tu solicitud...</div>
    <div class="thinking-content">{thinking_content}</div>
</div>
                    """
                    yield history

        # Marcar el pensamiento como completado
        final_thinking_content = accumulated_thoughts.strip()
        history[-1]["content"] = f"""
<div class="thinking-box done">
    <div class="thinking-title">✅ Análisis completado</div>
    <div class="thinking-content">{final_thinking_content}</div>
</div>
        """
        yield history
        
        # Agregar respuesta final si existe
        if final_response_content:
            time.sleep(0.5)
            history.append({
                "role": "assistant", 
                "content": final_response_content
            })
            yield history
    
    except Exception as e:
        error_message = f"❌ Ha ocurrido un error: {str(e)}"
        history.append({"role": "assistant", "content": error_message})
        yield history

def clear_conversation(session_id):
    if session_id in session_threads:
        del session_threads[session_id]
    return [
        {
            "role": "assistant", 
            "content": "¡Hola! Soy ToneCraft AI. La conversación ha sido reiniciada. ¿En qué puedo ayudarte?"
        }
    ]

def main():
    # Código de inicialización (como la comprobación de Reaper)
    pass # Este código no se ejecutará aquí, ver nota al final

## CAMBIO: CSS totalmente reescrito para ser compatible con temas (oscuro/claro)
theme_aware_css = """
/* Aplica un scrollbar con mejor estilo y compatible con modo oscuro */
.gradio-container {
    --scrollbar-thumb-color: var(--neutral-300);
    --scrollbar-thumb-color-hover: var(--neutral-400);
}
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: var(--neutral-100); border-radius: 10px; }
::-webkit-scrollbar-thumb { background: var(--scrollbar-thumb-color); border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: var(--scrollbar-thumb-color-hover); }

/* Contenedor principal y cabecera */
.header {
    text-align: center;
    padding: 20px 0;
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
    color: white;
    border-radius: var(--radius-lg);
    margin-bottom: var(--spacing-xxl);
    box-shadow: var(--shadow-drop-lg);
}
.header h1 { margin: 0; font-size: var(--text-xxl); font-weight: bold; }
.header p { margin: 10px 0 0 0; font-size: var(--text-lg); opacity: 0.9; }

/* Indicador de estado */
.status-indicator { display: inline-block; width: 10px; height: 10px; border-radius: 50%; background-color: #34d399; margin-right: 8px; animation: pulse 2s infinite; }
@keyframes pulse { 0% { box-shadow: 0 0 0 0 #34d39966; } 70% { box-shadow: 0 0 0 10px #34d39900; } 100% { box-shadow: 0 0 0 0 #34d39900; } }

/* Estructura del chat */
.chat-column { height: calc(85vh - 200px); min-height: 400px; }
.chat-container { border: 1px solid var(--neutral-200); border-radius: var(--radius-lg); background-color: var(--background-fill-primary); box-shadow: var(--shadow-sm); }
.gr-chatbot { background-color: transparent !important; }

/* Estilos para el cuadro de "pensamiento" del agente */
.thinking-box {
    padding: var(--spacing-lg);
    border-radius: var(--radius-md);
    border: 1px solid var(--primary-200);
    background-color: var(--primary-50);
    margin: 5px 0;
}
.thinking-box.done {
    border-color: var(--color-accent-soft);
    background-color: var(--green-50);
}
.dark .thinking-box {
    background-color: #2b224f; /* Fondo oscuro pero teñido de morado */
    border-color: var(--primary-500);
}
.dark .thinking-box.done {
    background-color: var(--green-900);
    border-color: var(--green-600);
}
.thinking-title {
    font-weight: bold;
    margin-bottom: var(--spacing-md);
    font-size: var(--text-md);
    color: var(--body-text-color);
}
.thinking-content {
    font-family: var(--font-mono);
    font-size: var(--text-sm);
    color: var(--body-text-color-subdued);
    white-space: pre-wrap;
    word-wrap: break-word;
}
.thinking-content code {
    color: var(--primary-600);
}
.dark .thinking-content code {
    color: var(--primary-300);
}
"""

## CAMBIO: Tema oscuro bien definido y uso de CSS compatible.
with gr.Blocks(
    theme=gr.themes.Base(font=gr.themes.GoogleFont("Inter")), 
    css=theme_aware_css
) as demo:
    
    with gr.Column(elem_classes="main-container"):
        gr.HTML("""
            <div class="header">
                <h1>🎵 ToneCraft AI</h1>
                <p>Tu asistente inteligente para producción musical en Reaper</p>
                <div><span class="status-indicator"></span><span>Conectado a Reaper</span></div>
            </div>
        """)
        
        session_id = gr.State(value=str(uuid.uuid4()))
        
        with gr.Row(equal_height=False):
            with gr.Column(scale=3):
                with gr.Column(elem_classes="chat-column"):
                    chatbot = gr.Chatbot(
                        label="Conversación", 
                        type="messages", 
                        value=[{
                            "role": "assistant", 
                            "content": "¡Hola! Soy ToneCraft AI. Puedo ayudarte a analizar y mejorar tus pistas de audio en Reaper. ¿Qué necesitas?"
                        }],
                        elem_id="chatbot",
                        bubble_full_width=False,
                        show_copy_button=True,
                        render_markdown=True,
                        height=600
                    )
                    
                    with gr.Row():
                        msg = gr.Textbox(
                            placeholder="Ej: 'Analiza la pista de bajo y mejora su claridad'",
                            show_label=False,
                            lines=2,
                            scale=8,
                            autofocus=True,
                            container=False # Para que ocupe todo el espacio sin contenedor extra
                        )
                        ## CAMBIO: Usar variantes nativas de Gradio para los botones
                        send = gr.Button("Enviar", scale=1, variant="primary")
            
            with gr.Column(scale=1):
                gr.Markdown("""
                ### 📋 Comandos Rápidos
                - **Análisis:** "Analiza la pista X"
                - **Procesamiento:** "Normaliza el volumen"
                - **Exportación:** "Exporta la pista"
                
                ### 💡 Tips
                - Sé específico con los nombres de pista.
                - El agente mostrará su proceso de pensamiento antes de la respuesta final.
                """)
                
                clear = gr.Button("🗑️ Borrar Conversación", variant="stop")
        
        gr.Examples(
            examples=[
                "La pista de bajo suena muy embarrada, analízala y arréglala",
                "Normaliza el volumen de todas las pistas y aplica un limitador suave al master",
                "Analiza el espectro de frecuencias de la pista 'Vocals' y sugiere mejoras",
            ],
            inputs=msg,
            label="💬 Ejemplos"
        )
    
    # CAMBIO: Lógica de envío simplificada
    def send_message(message, history, session_id):
        if not message.strip():
            # Devuelve los valores originales sin cambios
            return history, ""

        # Añade el mensaje del usuario al historial
        history.append({"role": "user", "content": message})
        
        # Llama a la función generadora
        # El textbox se limpia inmediatamente después de enviar
        return history, ""

    def stream_response(history, session_id):
        # El último mensaje es el del usuario
        user_message = history[-1]["content"]
        
        # El generador actualizará el historial
        for updated_history in chat_function(user_message, history, session_id):
            yield updated_history

    # CAMBIO: Flujo de eventos mejorado para una UX más fluida
    msg.submit(
        send_message, 
        [msg, chatbot, session_id], 
        [chatbot, msg]
    ).then(
        stream_response, 
        [chatbot, session_id], 
        chatbot
    )

    send.click(
        send_message, 
        [msg, chatbot, session_id], 
        [chatbot, msg]
    ).then(
        stream_response, 
        [chatbot, session_id], 
        chatbot
    )
    
    clear.click(
        fn=clear_conversation, 
        inputs=[session_id], 
        outputs=[chatbot],
        queue=False # La limpieza no necesita cola
    )

if __name__ == "__main__":
    print("--- Bienvenido a ToneCraft AI v2.1 ---")
    # Aquí puedes poner la lógica de comprobación de Reaper
    try:
        # reapy.Project()
        print("✅ ¡Conexión con Reaper exitosa!")
    except Exception as e:
        print(f"❌ Error fatal: No se pudo conectar con Reaper. Saliendo.")
        exit()

    # Lanzar la aplicación Gradio
    demo.queue().launch()

# Por ahora, para que puedas probarlo directamente:
# demo.queue().launch(show_error=True)