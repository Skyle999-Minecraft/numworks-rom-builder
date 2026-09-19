"""Preferences locales, sans ROM embarquee et sans ecriture dans les projets."""
import json
import os
from pathlib import Path
import tempfile

from builder import PLATFORMS, ROOT


def default_path():
    base = Path(os.environ.get("LOCALAPPDATA", Path.home() / ".config"))
    return base / "NumWorksRomBuilder" / "settings.json"


def defaults():
    return {"platform": "nes", "destination": str(ROOT), "compile_app": True,
            "paths": {key: [] for key in PLATFORMS}, "last_result": ""}


def load(path):
    result = defaults()
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return result
    if not isinstance(data, dict):
        return result
    if isinstance(data.get("platform"), str) and data["platform"] in PLATFORMS:
        result["platform"] = data["platform"]
    for key in ("destination", "last_result"):
        value = data.get(key)
        if isinstance(value, str) and value and "\0" not in value and Path(value).is_absolute():
            result[key] = value
    if isinstance(data.get("compile_app"), bool):
        result["compile_app"] = data["compile_app"]
    if isinstance(data.get("paths"), dict):
        for key, config in PLATFORMS.items():
            values = data["paths"].get(key, [])
            if not isinstance(values, list):
                continue
            for value in values:
                if (isinstance(value, str) and "\0" not in value and Path(value).is_absolute()
                        and Path(value).suffix.lower() in config.extensions
                        and value not in result["paths"][key]):
                    result["paths"][key].append(value)
                    if len(result["paths"][key]) == 64:
                        break
    return result


def save(path, data):
    """Remplacement atomique : une ecriture interrompue ne tronque pas l'ancien JSON."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=".settings-", suffix=".tmp", delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)