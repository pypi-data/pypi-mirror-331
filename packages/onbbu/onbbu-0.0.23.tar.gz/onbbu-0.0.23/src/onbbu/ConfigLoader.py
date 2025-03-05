import os
import importlib.util


class ConfigLoader:
    def __init__(self, base_dir):
        self.base_dir = base_dir

    def load_python_config(self, relative_path, attribute_name, default=None):
        """Upload a configuration file in Python format"""

        config_path = os.path.join(self.base_dir, *relative_path.split("/"))

        if not os.path.exists(config_path):
            print(
                f"⚠️ Advertencia: No se encontró `{relative_path}`. Se usará el valor por defecto."
            )
            return default

        spec = importlib.util.spec_from_file_location("config_module", config_path)

        config_module = importlib.util.module_from_spec(spec)
        
        spec.loader.exec_module(config_module)

        return getattr(config_module, attribute_name, default)
