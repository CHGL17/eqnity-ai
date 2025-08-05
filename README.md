# EQnity AI - Tu Asistente Inteligente de Producción Musical

![EQnity UI](assets/eqnity.png)

**EQnity AI** es un agente inteligente diseñado para integrarse con el DAW [Reaper](https://www.reaper.fm/), actuando como un asistente de ingeniero de sonido. Su objetivo es simplificar y democratizar la producción musical, permitiendo tanto a principiantes como a expertos mejorar sus mezclas a través de comandos en lenguaje natural.

## La Inspiración

> Como músico ocasional, siempre he soñado con conseguir tonos similares a los de mis ídolos. Sin embargo, esto requiere profundos conocimientos de producción musical para obtener resultados profesionales. Combinando mis conocimientos en inteligencia artificial y la experimentación con plugins VST, nace **EQnity**: un agente para hacer la producción musical más accesible para todos.

## ✨ Capacidades Principales

EQnity combina un agente conversacional (LLM) con un conjunto de herramientas (LangChain/LangGraph) que interactúan directamente con tu proyecto de Reaper.

*   **Control de VSTs:**
    *   Lista todas las pistas y sus plugins VST.
    *   Añade o elimina VSTs de cualquier pista.
    *   Lee y modifica múltiples parámetros de un VST en una sola acción.
*   **Análisis de Audio Inteligente:**
    *   **Diagnóstico en Reaper:** Renderiza un fragmento de una pista, lo analiza (Loudness, brillo espectral) y utiliza esa información para tomar decisiones informadas.
    *   **Análisis de Archivos:** Permite subir un archivo de audio para obtener un análisis detallado y sugerencias de procesamiento basadas en Machine Learning (`librosa`).
*   **Interfaz de Usuario Intuitiva:**
    *   Una interfaz de chat simple construida con Gradio.
    *   Visualización del "proceso de pensamiento" del agente, mostrando qué herramientas utiliza y por qué.
    *   Controles para análisis de audio con un solo clic.

## 🏛️ Arquitectura del Proyecto

EQnity está construido sobre una arquitectura moderna que separa la lógica del agente, las herramientas y la interfaz de usuario.

1.  **Interfaz de Usuario (`ui.py`):**
    *   Construida con **Gradio** para una rápida implementación de una interfaz web interactiva.
    *   Gestiona la conversación y las interacciones con los componentes de análisis de ML.

2.  **Agente Inteligente (`agent/main.py`):**
    *   Utiliza **LangGraph** para crear un agente ReAct (Reasoning and Acting).
    *   El LLM (configurado para `deepseek` vía OpenRouter) interpreta la solicitud del usuario.
    *   El prompt (`agent/prompt.py`) guía al agente para que primero diagnostique los problemas de audio antes de actuar.

3.  **Herramientas (`tools/`):**
    *   **`vst_tools.py`:** Interactúa con Reaper a través de la librería **`reapy`** para manipular pistas y plugins.
    *   **`audio_tools.py`:** Orquesta el renderizado de audio desde Reaper y su análisis con **`pyloudnorm`** y **`librosa`**.
    *   **`ml_tools.py`:** Contiene funciones para el análisis de archivos de audio subidos por el usuario.

4.  **Núcleo (`core/`):**
    *   Contiene utilidades compartidas (`core/utils.py`) y modelos de datos Pydantic (`core/models.py`) para una estructura robusta.

## 🚀 Cómo Empezar

**Prerrequisitos:**
*   Python 3.8+
*   Reaper DAW instalado.
*   Una clave de API de OpenRouter.

### Configuración de Reaper para `reapy`

Para que EQnity pueda comunicarse con Reaper, es necesario configurar `reapy` correctamente. Sigue estos pasos:

1.  **Instalar el manejador de plugins [ReaPack](https://reapack.com/)**.
2.  Dentro de Reaper, ve a `Extensions > ReaPack > Browse packages` e instala los siguientes paquetes:
    *   `ReaMCULive: Programmable ReaScript API control surface`
    *   `is_ReaScriptAPI: API functions for ReaScripts`
    *   `ReaImGui: ReaScript binding for Dear ImGUI`
3.  Ve a `Options > Preferences > ReaScript`:
    *   En la pestaña `Python`, asegúrate de que `Enable Python for use with ReaScript` esté activado.
    *   Configura la ruta a tu DLL de Python si no se detecta automáticamente.
4.  Ve a `Options > Preferences > Control/OSC/Web`:
    *   Verificar que exista una `Web browser interface` con el puerto `2307`, en caso de que no:
        -   Haz clic en `Add` y crea una nueva interfaz.
        -   En `Control surface mode`, selecciona `Web browser interface`. Esto debería usar el puerto `2307` por defecto, que `reapy` utiliza para comunicarse.

**Instalación:**

1.  Clona el repositorio:
    ```bash
    git clone https://github.com/tu-usuario/eqnity-ai.git
    cd eqnity-ai
    ```

2.  Crea un entorno virtual (opcional pero recomendado):
    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows usa `venv\Scripts\activate`
    ```

3.  Instala las dependencias:
    ```bash
    pip install -r requirements.txt
    ```

4.  Configura tus variables de entorno. Crea un archivo `.env` en la raíz del proyecto:
    ```
    OPENROUTER_API_KEY="tu_clave_de_api_aqui"
    ```

5.  Ejecuta la aplicación:
    ```bash
    python main.py
    ```
    La aplicación se iniciará y podrás acceder a ella desde tu navegador. ¡Asegúrate de que Reaper esté abierto!

## 🗺️ Futuro del Proyecto (Roadmap)

EQnity está en continuo desarrollo. Las próximas grandes características planeadas son:

*   [ ] **Separación de Stems:** Integrar un modelo como Spleeter para separar automáticamente una pista en vocales, bajo, batería, etc. (ya existe un placeholder en `tools/ml_tools.py`).
*   [ ] **Aprendizaje de Presets:** Capacidad para analizar los presets de VST de tus artistas favoritos y aplicar estilos similares a tus pistas.
*   [ ] **Análisis Espectral Avanzado:** Generar y mostrar gráficos del espectro de frecuencia directamente en la interfaz.
*   [ ] **Soporte para más DAWs:** Explorar la integración con otros DAWs populares como Ableton Live o FL Studio.

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Si tienes ideas para nuevas funcionalidades, mejoras o has encontrado un bug, por favor sigue estos pasos:

1.  Haz un Fork del repositorio.
2.  Crea tu rama para la nueva funcionalidad (`git checkout -b feature/amazing-feature`).
3.  Haz commit de tus cambios (`git commit -m 'Añade una increíble funcionalidad'`).
4.  Haz push a la rama (`git push origin feature/amazing-feature`).
5.  Abre un Pull Request detallando tus cambios y la nueva funcionalidad.