from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from canopy.config import ensure_dir, utc_timestamp


class ExperimentRegistry:
    def __init__(self, root: str | Path = "results/experiments") -> None:
        self.root = ensure_dir(root)

    def register(self, experiment_id: str, metadata: dict[str, Any]) -> Path:
        payload = {
            "experiment_id": experiment_id,
            "timestamp": utc_timestamp(),
            **metadata,
        }
        digest = hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()[:12]
        path = self.root / f"{experiment_id}_{digest}.json"
        with path.open("w") as f:
            json.dump(payload, f, indent=2, default=str)
        return path
