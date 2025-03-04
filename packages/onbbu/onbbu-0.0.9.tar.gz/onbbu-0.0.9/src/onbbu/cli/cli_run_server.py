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

        print(f"🚀 Iniciando servidor en {module.server.host}:{module.server.port} ...")

        uvicorn.run(
            "internal.main:ServerHttp.server",
            host=module.server.host,
            port=module.server.port,
            reload=module.server.reload,
            workers=module.server.workers,
        )

    else:
        print("❌ `internal/main.py` no contiene una instancia `server`.")
