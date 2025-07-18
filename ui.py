import uuid
import gradio as gr
from styles import theme_aware_css
from chat import chat_function, clear_conversation

def build_ui():
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
                                container=False
                            )
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

        def send_message(message, history, session_id):
            if not message.strip():
                return history, ""
            history.append({"role": "user", "content": message})
            return history, ""

        def stream_response(history, session_id):
            user_message = history[-1]["content"]
            for updated_history in chat_function(user_message, history, session_id):
                yield updated_history

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
            queue=False
        )

    return demo