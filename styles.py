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
    background: linear-gradient(90deg, rgb(7, 174, 234) 0%, rgb(43, 245, 152) 100%);
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