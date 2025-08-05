import os
import uuid
import base64
import gradio as gr
from styles import theme_aware_css
from chat import chat_function, clear_conversation, update_language
from tools.ml_tools import analyze_uploaded_audio, suggest_audio_processing, separate_audio_placeholder
from i18n.utils import i18n, t

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
            # Header con soporte dinámico de idioma
            header_html = gr.HTML(elem_id="header-container")
            
            def update_header():
                return f"""
                    <div class="header">
                        {f"<img src='data:image/png;base64,{get_image_base64('assets/eqnity.png')}' alt='EQnity AI Logo' style='height:64px;width:64px;'>"}
                        <div>
                            <h1>{t('app_title')}</h1>
                            <p>{t('app_subtitle')}</p>
                        </div>
                    </div>
                """

            session_id = gr.State(value=str(uuid.uuid4()))
            
            # Selector de idioma
            with gr.Row():
                language_selector = gr.Dropdown(
                    choices=[("Español", "es"), ("English", "en")],
                    value=i18n.current_lang,
                    label=t('language'),
                    scale=1
                )
            
            with gr.Row(equal_height=False):
                with gr.Column(scale=3):
                    with gr.Column(elem_classes="chat-column"):
                        chatbot = gr.Chatbot(
                            label=t('conversation'),
                            type="messages",
                            value=[{
                                "role": "assistant",
                                "content": t('welcome_message')
                            }],
                            elem_id="chatbot",
                            bubble_full_width=False,
                            show_copy_button=True,
                            render_markdown=True,
                            height=600
                        )
                        with gr.Row():
                            msg = gr.Textbox(
                                placeholder=t('input_placeholder'),
                                show_label=False,
                                lines=2,
                                scale=8,
                                autofocus=True,
                                container=False
                            )
                            send = gr.Button(t('send'), scale=1, variant="primary")
                
                with gr.Column(scale=1):
                    # Sección de análisis ML
                    with gr.Column():
                        ml_analysis_label = gr.Markdown(f"### {t('ml_analysis')}")
                        audio_upload = gr.Audio(
                            label=t('audio_track'),
                            type="filepath",
                            elem_id="audio-player",
                            autoplay=False,
                            show_download_button=True,
                        )
                        
                        with gr.Row(elem_classes='button-row'):
                            analyze_btn = gr.Button(t('analyze'), scale=1, variant="primary")
                            suggest_btn = gr.Button(t('suggest_processing'), scale=1, variant="secondary")
                            separate_btn = gr.Button(t('separate_instruments'), scale=1, variant="secondary")

                    clear = gr.Button(t('clear_conversation'), variant='huggingface')
            
            # Ejemplos - usando un Markdown en lugar de Examples para poder actualizarlo
            examples_markdown = gr.Markdown(elem_id="examples-section")
            
            def get_examples_html():
                return f"""
### {t('examples_title')}
- {t('example_1')}
- {t('example_2')}
- {t('example_3')}
                """
            
            # Información adicional
            info_markdown = gr.Markdown(elem_id="info-markdown")
            
            def update_info_text():
                return f"""
### {t('quick_commands')}
- {t('analysis_cmd')}
- {t('processing_cmd')}
- {t('export_cmd')}

### {t('ml_analysis')}
- {t('upload_audio_first')}
- Obtén sugerencias de procesamiento basadas en características del audio
- Separación de instrumentos (próximamente)

### {t('tips')}
{t('tip_specific')}
{t('tip_thinking')}
                """

        # Funciones existentes actualizadas
        def send_message(message, history, session_id):
            if not message.strip():
                return history, ""
            history.append({"role": "user", "content": message})
            return history, ""

        def stream_response(history, session_id):
            user_message = history[-1]["content"]
            for updated_history in chat_function(user_message, history, session_id):
                yield updated_history

        # Funciones ML actualizadas
        def handle_analyze_audio(audio_path, history):
            if not audio_path:
                history.append({"role": "assistant", "content": t('upload_audio_first')})
                return history
            
            history.append({"role": "user", "content": f"{t('analyze_audio')}: {os.path.basename(audio_path)}"})
            result = analyze_uploaded_audio.invoke({"audio_path": audio_path})
            history.append({"role": "assistant", "content": result})
            return history

        def handle_suggest_processing(audio_path, history):
            if not audio_path:
                history.append({"role": "assistant", "content": t('upload_audio_first')})
                return history
            
            history.append({"role": "user", "content": f"{t('suggest_processing_for')}: {os.path.basename(audio_path)}"})
            result = suggest_audio_processing.invoke({"audio_path": audio_path})
            history.append({"role": "assistant", "content": result})
            return history

        def handle_separate_audio(audio_path, history):
            if not audio_path:
                history.append({"role": "assistant", "content": t('upload_audio_first')})
                return history
            
            history.append({"role": "user", "content": f"{t('separate_instruments_from')}: {os.path.basename(audio_path)}"})
            result = separate_audio_placeholder(audio_path)
            history.append({"role": "assistant", "content": result})
            return history

        # Función para cambiar idioma
        def change_language(lang_value, history):
            update_language(lang_value)
            
            # Actualizar el mensaje inicial del chatbot
            new_history = [{
                "role": "assistant",
                "content": t('welcome_message')
            }]
            
            # Retornar todos los componentes actualizados
            return (
                update_header(),  # header_html
                new_history,  # chatbot value
                gr.update(label=t('conversation')),  # chatbot label
                gr.update(placeholder=t('input_placeholder')),  # msg
                gr.update(value=t('send')),  # send button
                gr.update(label=t('audio_track')),  # audio_upload
                gr.update(value=t('analyze')),  # analyze_btn
                gr.update(value=t('suggest_processing')),  # suggest_btn
                gr.update(value=t('separate_instruments')),  # separate_btn
                gr.update(value=t('clear_conversation')),  # clear button
                f"### {t('ml_analysis')}",  # ml_analysis_label
                get_examples_html(),  # examples_markdown
                update_info_text(),  # info_markdown
                gr.update(label=t('language'))  # language_selector
            )

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

        # Event handlers ML
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

        # Event handler para cambio de idioma
        language_selector.change(
            fn=change_language,
            inputs=[language_selector, chatbot],
            outputs=[
                header_html,
                chatbot,
                chatbot,
                msg,
                send,
                audio_upload,
                analyze_btn,
                suggest_btn,
                separate_btn,
                clear,
                ml_analysis_label,
                examples_markdown,
                info_markdown,
                language_selector
            ]
        )

        # Cargar valores iniciales
        demo.load(
            fn=lambda: (update_header(), get_examples_html(), update_info_text()),
            outputs=[header_html, examples_markdown, info_markdown]
        )

    return demo