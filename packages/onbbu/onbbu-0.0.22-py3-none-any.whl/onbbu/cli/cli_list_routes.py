from onbbu.settings.ConfigLoader import ConfigLoader
from onbbu.settings import BASE_DIR


def list_routes():
    """List all server routes"""

    module = ConfigLoader(BASE_DIR).load_python_config(
        relative_path="internal/main.py",
        attribute_name="server",
        default=[],
    )

    if hasattr(module, "server"):
        print("📌 Rutas registradas:")
        for route in module.server.http.routes:
            print(f"➡ {route.path} - {route.methods}")
    else:
        print("❌ `internal/main.py` no contiene una instancia `server`.")
