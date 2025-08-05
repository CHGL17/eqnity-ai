import os
import uuid
import base64
import gradio as gr
from styles import theme_aware_css
from chat import chat_function, clear_conversation
from tools.ml_tools import analyze_uploaded_audio, suggest_audio_processing, separate_audio_placeholder

def get_image_base64(image_path):
    """Convierte una imagen a base64 para embedder en HTML"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception:
        return None

def build_ui():
    with gr.Blocks(
        theme=gr.themes.Base(font=gr.themes.GoogleFont("Inter")),
        css=theme_aware_css
    ) as demo:
        with gr.Column(elem_classes="main-container"):
            gr.HTML(f"""
                <div class="header">
                    {f"<img src='data:image/png;base64,{get_image_base64('assets/eqnity.png')}' alt='EQnity AI Logo' style='height:64px;width:64px;'>"}
                    <div>
                        <h1>EQnity AI</h1>
                        <p>Tu asistente inteligente para producción musical en Reaper</p>
                    </div>
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
                                "content": "¡Hola! Soy EQnity AI. Puedo ayudarte a analizar y mejorar tus pistas de audio en Reaper. ¿Qué necesitas?"
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
                    # Sección de análisis ML
                    with gr.Column():
                        gr.Markdown("### 🤖 Análisis con ML")
                        audio_upload = gr.Audio(
                            label="Pista de Audio",
                            type="filepath",
                            elem_id="audio-player",
                            autoplay=False,
                            show_download_button=True,
                        )
                        
                        with gr.Row(elem_classes='button-row'):
                            analyze_btn = gr.Button("🔍 Analizar", scale=1, variant="primary")
                            suggest_btn = gr.Button("💡 Sugerir procesamiento", scale=1, variant="secondary")
                            separate_btn = gr.Button("🎵 Separar instrumentos", scale=1, variant="secondary")

                    clear = gr.Button("🗑️ Borrar Conversación", variant='huggingface')
            
            gr.Examples(
                examples=[
                    "La pista de bajo suena muy embarrada, analízala y arréglala",
                    "Normaliza el volumen de todas las pistas y aplica un limitador suave al master",
                    "Analiza el espectro de frecuencias de la pista 'Vocals' y sugiere mejoras",
                ],
                inputs=msg,
                label="💬 Ejemplos"
            )
            
            gr.Markdown("""
            ### 📋 Comandos Rápidos
            - **Análisis:** "Analiza la pista X"
            - **Procesamiento:** "Normaliza el volumen"
            - **Exportación:** "Exporta la pista"
            
            ### 🤖 Análisis ML
            - Sube un audio para análisis automático con machine learning
            - Obtén sugerencias de procesamiento basadas en características del audio
            - Separación de instrumentos (próximamente)
            
            ### 💡 Tips
            - Sé específico con los nombres de pista.
            - El agente mostrará su proceso de pensamiento antes de la respuesta final.
            """)

        # Funciones existentes
        def send_message(message, history, session_id):
            if not message.strip():
                return history, ""
            history.append({"role": "user", "content": message})
            return history, ""

        def stream_response(history, session_id):
            user_message = history[-1]["content"]
            for updated_history in chat_function(user_message, history, session_id):
                yield updated_history

        # Funciones ML nuevas
        def handle_analyze_audio(audio_path, history):
            if not audio_path:
                history.append({"role": "assistant", "content": "Por favor, sube un archivo de audio primero."})
                return history
            
            # Agregar mensaje del usuario simulado
            history.append({"role": "user", "content": f"Analiza el audio: {os.path.basename(audio_path)}"})
            
            # Obtener y agregar respuesta del análisis
            result = analyze_uploaded_audio.invoke({"audio_path": audio_path})
            history.append({"role": "assistant", "content": result})
            return history

        def handle_suggest_processing(audio_path, history):
            if not audio_path:
                history.append({"role": "assistant", "content": "Por favor, sube un archivo de audio primero."})
                return history
            
            history.append({"role": "user", "content": f"Sugiere procesamiento para: {os.path.basename(audio_path)}"})
            result = suggest_audio_processing.invoke({"audio_path": audio_path})
            history.append({"role": "assistant", "content": result})
            return history

        def handle_separate_audio(audio_path, history):
            if not audio_path:
                history.append({"role": "assistant", "content": "Por favor, sube un archivo de audio primero."})
                return history
            
            history.append({"role": "user", "content": f"Separa instrumentos de: {os.path.basename(audio_path)}"})
            result = separate_audio_placeholder(audio_path)
            history.append({"role": "assistant", "content": result})
            return history

        # Event handlers existentes
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

        # Event handlers ML nuevos
        analyze_btn.click(
            handle_analyze_audio,
            inputs=[audio_upload, chatbot],
            outputs=[chatbot]
        )

        suggest_btn.click(
            handle_suggest_processing,
            inputs=[audio_upload, chatbot],
            outputs=[chatbot]
        )

        separate_btn.click(
            handle_separate_audio,
            inputs=[audio_upload, chatbot],
            outputs=[chatbot]
        )

    return demo