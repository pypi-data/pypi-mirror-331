import uvicorn
from onbbu.settings.ConfigLoader import ConfigLoader
from onbbu.settings.main import BASE_DIR


def run_server():
    """Ejecuta `internal/main.py` como servidor"""

    module = ConfigLoader(BASE_DIR).load_python_config(
        relative_path="internal/main.py",
        attribute_name="server",
        default=[],
    )

    if hasattr(module, "server"):
        print("🚀 Iniciando FastAPI desde `internal/main.py`...")

        print(f"🚀 Iniciando servidor en {module.host}:{module.port} ...")

        uvicorn.run(
            "internal.main:server",
            host=module.host,
            port=module.port,
            reload=module.reload,
            workers=module.workers,
        )

    else:
        print("❌ `internal/main.py` no contiene una instancia `server`.")
