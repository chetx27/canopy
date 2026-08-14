from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


def load_config(path: str | Path, base_dir: str | Path | None = None) -> dict[str, Any]:
    path = Path(path)
    base_dir = Path(base_dir or path.parent)
    with path.open() as f:
        cfg = yaml.safe_load(f)
    if "extends" in cfg:
        parent_name = cfg.pop("extends")
        parent_path = base_dir / parent_name
        if not parent_path.suffix:
            parent_path = parent_path.with_suffix(".yaml")
        parent = load_config(parent_path, base_dir=base_dir)
        merged = _deep_merge(parent, cfg)
        return merged
    return cfg


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    out = dict(base)
    for key, value in override.items():
        if key in out and isinstance(out[key], dict) and isinstance(value, dict):
            out[key] = _deep_merge(out[key], value)
        else:
            out[key] = value
    return out


def ensure_dir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def save_json(path: str | Path, payload: dict[str, Any]) -> None:
    path = Path(path)
    ensure_dir(path.parent)
    with path.open("w") as f:
        json.dump(payload, f, indent=2, default=str)
