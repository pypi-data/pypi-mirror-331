import uvicorn

from onbbu.logger import LogLevel
from onbbu.settings.ConfigLoader import ConfigLoader
from onbbu.settings import BASE_DIR, logger


def run_server():
    """Ejecuta `internal/main.py` como servidor"""

    module = ConfigLoader(BASE_DIR).load_python_config(
        relative_path="internal/main.py",
        attribute_name="server",
        default=[],
    )

    if hasattr(module, "server"):
        logger.log(
            level=LogLevel.INFO,
            message=f"🚀 Iniciando servidor en {module.host}:{module.port} ...",
        )

        for route in module.server.routes:
            logger.log(
                level=LogLevel.INFO,
                message=f"🔗 {route.path} -> {route.name} ({route.methods})",
            )

        uvicorn.run(
            "internal.main:server.server",
            host=module.host,
            port=module.port,
            reload=module.reload,
            workers=module.workers,
        )

    else:
        logger.log(
            level=LogLevel.ERROR,
            message=f"❌ `internal/main.py` no contiene una instancia `server`.",
        )
