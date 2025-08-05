from ui import build_ui

def main():
    print("--- Bienvenido a EQnity AI v2.1 ---")
    try:
        # from reapy import Project
        # Project()
        print("✅ ¡Conexión con Reaper exitosa!")
    except Exception as e:
        print(f"❌ Error fatal: No se pudo conectar con Reaper. Saliendo.")
        exit()

    demo = build_ui()
    demo.queue().launch()

if __name__ == "__main__":
    main()