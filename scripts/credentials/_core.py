"""Core helpers shared by credential command modules."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ._config import DEFAULT_NAMESPACE, SECRET_FIELDS, namespace_dir, validate_namespace
from ._minimal import CredentialError, MinimalCredentialManager

_MANAGERS: dict[str, MinimalCredentialManager] = {}


def get_manager(namespace: str = DEFAULT_NAMESPACE) -> MinimalCredentialManager:
    namespace = validate_namespace(namespace)
    if namespace not in _MANAGERS:
        _MANAGERS[namespace] = MinimalCredentialManager(namespace)
    return _MANAGERS[namespace]


def get(namespace: str, key: str, default: Any = None) -> Any:
    return get_manager(namespace).get(key, default)


def set(namespace: str, key: str, value: Any) -> None:
    get_manager(namespace).set(key, value)


def delete(namespace: str, key: str) -> bool:
    return get_manager(namespace).delete(key)


def list_all(namespace: str) -> dict[str, Any]:
    return get_manager(namespace).list_all()


def mask_secret(data: Any) -> Any:
    if isinstance(data, dict):
        return {key: mask_secret(value) if key not in SECRET_FIELDS else "****" for key, value in data.items()}
    if isinstance(data, list):
        return [mask_secret(item) for item in data]
    if isinstance(data, str):
        return "****"
    return data


def masked_list(namespace: str) -> dict[str, Any]:
    return mask_secret(list_all(namespace))


def load_json(path: Path, default: Any) -> Any:
    if not path.is_file():
        return default
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default
    return data


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def config_path(namespace: str, filename: str) -> Path:
    return namespace_dir(namespace, create=True) / filename


__all__ = [
    "CredentialError",
    "config_path",
    "delete",
    "get",
    "get_manager",
    "list_all",
    "load_json",
    "mask_secret",
    "masked_list",
    "namespace_dir",
    "save_json",
    "set",
]
