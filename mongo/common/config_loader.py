import os
import re
from pathlib import Path

import yaml
from dotenv import load_dotenv

# Matches ${NAME} and ${NAME:-default}.
_VAR_PATTERN = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)(?::-([^}]*))?\}")

DEFAULT_CONFIG = Path(__file__).resolve().parents[1] / "config.yaml"


def _expand(value):
    if isinstance(value, dict):
        return {key: _expand(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_expand(item) for item in value]
    if not isinstance(value, str):
        return value

    def replace(match):
        name, default = match.group(1), match.group(2)
        if name in os.environ and os.environ[name] != "":
            return os.environ[name]
        if default is not None:
            return default
        raise KeyError(f"Missing environment variable: {name}")

    return _VAR_PATTERN.sub(replace, value)


def load_config(path=None):
    config_path = Path(path) if path else DEFAULT_CONFIG
    load_dotenv(config_path.parent / ".env")

    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle) or {}

    return _expand(config)
