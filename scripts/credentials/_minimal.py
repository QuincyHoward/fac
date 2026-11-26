"""Minimal Fernet-backed credential store."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ._config import namespace_dir, validate_namespace, _lock_down


class CredentialError(RuntimeError):
    """Raised when the encrypted store cannot be safely read or written."""


class MinimalCredentialManager:
    """Namespace-scoped Fernet credential store."""

    def __init__(self, namespace: str = "specx") -> None:
        self.namespace = validate_namespace(namespace)
        self.dir = namespace_dir(self.namespace, create=True)
        self.enc_file = self.dir / "credentials.enc"
        self.key_file = self.dir / ".secret_key"
        self.load_error: str | None = None
        self._fernet = self._init_fernet()
        self._store = self._load()

    def _init_fernet(self):
        try:
            from cryptography.fernet import Fernet
        except ImportError as exc:
            raise CredentialError(
                "cryptography is required; install requirements-dev.txt"
            ) from exc

        if self.key_file.exists():
            key = self.key_file.read_bytes()
        else:
            key = Fernet.generate_key()
            tmp = self.key_file.with_suffix(".tmp")
            tmp.write_bytes(key)
            tmp.replace(self.key_file)
            _lock_down(self.key_file)
        _lock_down(self.dir)
        return Fernet(key)

    def _load(self) -> dict[str, Any]:
        if not self.enc_file.exists():
            return {"__meta__": {"namespace": self.namespace}}
        try:
            ciphertext = self.enc_file.read_bytes()
            if not ciphertext:
                return {"__meta__": {"namespace": self.namespace}}
            data = json.loads(self._fernet.decrypt(ciphertext).decode("utf-8"))
            if not isinstance(data, dict):
                raise ValueError("credential store is not a JSON object")
            data.setdefault("__meta__", {"namespace": self.namespace})
            return data
        except Exception as exc:
            self.load_error = f"Unable to decrypt credential store: {exc}"
            return {}

    def _require_readable(self) -> None:
        if self.load_error:
            raise CredentialError(self.load_error)

    def _save(self) -> None:
        self._require_readable()
        plaintext = json.dumps(self._store, ensure_ascii=False).encode("utf-8")
        ciphertext = self._fernet.encrypt(plaintext)
        tmp = self.enc_file.with_suffix(".tmp")
        tmp.write_bytes(ciphertext)
        tmp.replace(self.enc_file)
        _lock_down(self.enc_file)

    def get(self, key: str, default: Any = None) -> Any:
        self._require_readable()
        return self._store.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._require_readable()
        self._store[key] = value
        self._save()

    def delete(self, key: str) -> bool:
        self._require_readable()
        if key not in self._store:
            return False
        self._store.pop(key, None)
        self._save()
        return True

    def list_all(self) -> dict[str, Any]:
        self._require_readable()
        return dict(self._store)

    def dir_path(self) -> Path:
        return Path(self.dir)
