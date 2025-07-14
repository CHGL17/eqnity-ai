import reapy
import uuid
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from agent.main import agent_executor

# --- 3. Interfaz de consola ---
def main():
    print("--- Bienvenido a ToneCraft AI v2.1 (modularizado con LangGraph) ---")
    print("Asegúrate de tener instaladas las librerías: librosa, numpy, soundfile, pyloudnorm")
    try:
        reapy.Project()
        print("¡Conexión con Reaper exitosa!")
    except Exception as e:
        print(f"Error fatal: No se pudo conectar con Reaper. ¿Está abierto y configurado?")
        return
    
    print("Escribe tu petición (o 'salir'). Ej: 'La pista de bajo suena muy embarrada, analízala y arréglala.'")
    
    # Configuración para mantener el hilo de conversación
    config = RunnableConfig(configurable={"thread_id": str(uuid.uuid4())}, run_id=uuid.uuid4())
    
    while True:
        user_query = input("\nUsuario > ")
        if user_query.lower() in ["salir", "exit", "quit"]:
            break
        if user_query:
            try:
                # Usar el nuevo formato con thread_id para persistencia
                input_message = HumanMessage(content=user_query)
                for event in agent_executor.stream(
                    {"messages": [input_message]}, 
                    config,
                    stream_mode="values"
                ):
                    # Mostrar solo las respuestas del asistente
                    if event["messages"] and event["messages"][-1].type == "ai":
                        print(f"\nToneCraft > {event['messages'][-1].content}")
            except Exception as e:
                print(f"\nHa ocurrido un error inesperado en el agente: {e}")

if __name__ == "__main__":
    main()
