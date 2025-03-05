import os
from autogen import config_list_from_json

class ConfigLoader:
    """Loads and caches OpenAI assistant configuration."""
    _config_list = None

    @classmethod
    def get_openai_config(cls):
        # Dynamically determine the path relative to the current file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_dir, "openai_assistant_config.json")

        if cls._config_list is None:
            if not os.path.exists(config_path):
                raise FileNotFoundError(f"Config file not found: {config_path}")
            cls._config_list = config_list_from_json(config_path)

        return {"config_list": cls._config_list}