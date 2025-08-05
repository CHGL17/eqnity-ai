# EQnity AI - Your Intelligent Music Production Assistant

![EQnity UI](assets/eqnity_logo.png)

**EQnity AI** is an intelligent agent designed to integrate with the [Reaper](https://www.reaper.fm/) DAW, acting as a sound engineer's assistant. Its goal is to simplify and democratize music production, allowing both beginners and experts to improve their mixes through natural language commands.

## The Inspiration

> As a casual musician, I've always dreamed of achieving tones similar to my idols. However, this requires deep knowledge of music production to get professional results. By combining my knowledge in artificial intelligence and experimentation with VST plugins, **EQnity** was born: an agent to make music production more accessible to everyone.

## ✨ Core Features

EQnity combines a conversational agent (LLM) with a set of tools (LangChain/LangGraph) that interact directly with your Reaper project.

*   **VST Control:**
    *   List all tracks and their VST plugins.
    *   Add or remove VSTs from any track.
    *   Read and modify multiple parameters of a VST in a single action.
*   **Intelligent Audio Analysis:**
    *   **In-Reaper Diagnostics:** Renders a snippet of a track, analyzes it (Loudness, spectral brightness), and uses that information to make informed decisions.
    *   **File Analysis:** Allows uploading an audio file to get a detailed analysis and processing suggestions based on Machine Learning (`librosa`).
*   **Intuitive User Interface:**
    *   A simple chat interface built with Gradio.
    *   Visualization of the agent's "thought process," showing which tools it uses and why.
    *   One-click controls for audio analysis.

## 🏛️ Project Architecture

EQnity is built on a modern architecture that separates the agent's logic, tools, and user interface.

1.  **User Interface (`ui.py`):**
    *   Built with **Gradio** for rapid implementation of an interactive web interface.
    *   Manages the conversation and interactions with the ML analysis components.

2.  **Intelligent Agent (`agent/main.py`):**
    *   Uses **LangGraph** to create a ReAct (Reasoning and Acting) agent.
    *   The LLM (configured for `deepseek` via OpenRouter) interprets the user's request.
    *   The prompt (`agent/prompt.py`) guides the agent to first diagnose audio issues before acting.

3.  **Tools (`tools/`):**
    *   **`vst_tools.py`:** Interacts with Reaper through the **`reapy`** library to manipulate tracks and plugins.
    *   **`audio_tools.py`:** Orchestrates audio rendering from Reaper and its analysis with **`pyloudnorm`** and **`librosa`**.
    *   **`ml_tools.py`:** Contains functions for analyzing user-uploaded audio files.

4.  **Core (`core/`):**
    *   Contains shared utilities (`core/utils.py`) and Pydantic data models (`core/models.py`) for a robust structure.

## 🚀 Getting Started

**Prerequisites:**
*   Python 3.8+
*   Reaper DAW installed.
*   An OpenRouter API key.

### Configuring Reaper for `reapy`

For EQnity to communicate with Reaper, you need to configure `reapy` correctly. Follow these steps:

1.  **Install the [ReaPack](https://reapack.com/) plugin manager**.
2.  Inside Reaper, go to `Extensions > ReaPack > Browse packages` and install the following packages:
    *   `ReaMCULive: Programmable ReaScript API control surface`
    *   `is_ReaScriptAPI: API functions for ReaScripts`
    *   `ReaImGui: ReaScript binding for Dear ImGUI`
3.  Go to `Options > Preferences > ReaScript`:
    *   On the `Python` tab, make sure `Enable Python for use with ReaScript` is checked.
    *   Set the path to your Python DLL if it's not detected automatically.
4.  Go to `Options > Preferences > Control/OSC/Web`:
    *   Verify that a `Web browser interface` exists on port `2307`. If not:
        -   Click `Add` and create a new interface.
        -   In `Control surface mode`, select `Web browser interface`. This should use port `2307` by default, which `reapy` uses to communicate.

**Installation:**

1.  Clone the repository:
    ```bash
    git clone https://github.com/your-user/eqnity-ai.git
    cd eqnity-ai
    ```

2.  Create a virtual environment (optional but recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4.  Set up your environment variables. Create a `.env` file in the project root:
    ```
    OPENROUTER_API_KEY="your_api_key_here"
    ```

5.  Run the application:
    ```bash
    python -m main
    ```
    The application will start, and you can access it from your browser. Make sure Reaper is running!

## 🗺️ Project Roadmap

EQnity is under continuous development. The next major planned features are:

*   [ ] **Knowledge Base:** Integrate a musical knowledge database (RAG) for more informed responses.
*   [ ] **Stem Separation:** Integrate a model like Spleeter to automatically separate a track into vocals, bass, drums, etc. (a placeholder already exists in `tools/ml_tools.py`).
*   [ ] **Preset Learning:** Ability to analyze VST presets from your favorite artists and apply similar styles to your tracks.
*   [ ] **Advanced Spectral Analysis:** Generate and display frequency spectrum graphs directly in the interface.
*   [ ] **Support for more DAWs:** Explore integration with other popular DAWs like Ableton Live or FL Studio.

## 🤝 Contributions

Contributions are welcome! If you have ideas for new features, improvements, or have found a bug, please follow these steps:

1.  Fork the repository.
2.  Create your feature branch (`git checkout -b feature/amazing-feature`).
3.  Commit your changes (`git commit -m 'Add an amazing feature'`).
4.  Push to the branch (`git push origin feature/amazing-feature`).
5.  Open a Pull Request detailing your changes and the new functionality.

## 📜 License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

When using this software or parts of it, you are required to include the original copyright notice and license information.

## Acknowledgements
-   [Reapy](https://github.com/RomeoDespres/reapy) for making the interaction with Reaper possible.