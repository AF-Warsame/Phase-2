# --- stdlib ---
from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any, Dict

# --- third-party ---
import typer

from .. import fetch_repo as fr

# --- local ---
from ..utils import _as_bool, _as_int
from .base import BaseHandler

log = logging.getLogger(__name__)


@dataclass
class ModelHandler(BaseHandler):
    model_id: str

    def fetch_data(self) -> Dict[str, Any]:
        log.info("Fetching HF model data: %s", self.model_id)
        data = fr.fetch_model_data(model_id=self.model_id)
        if not isinstance(data, dict):
            raise TypeError("fetch_model_data() must return a dict")
        return data

    def format_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        formatted: Dict[str, Any] = {
            "source": "huggingface",
            "id": data.get("modelId") or data.get("id") or self.model_id,
            "author": data.get("author") or data.get("owner") or "",
            "license": data.get("license") or "",
            "downloads": _as_int(data.get("downloads")),  # mock supplies this
            "last_modified": data.get("lastModified")
            or data.get("last_modified")
            or "",
            "has_readme": _as_bool(data.get("readme"))
            or _as_bool(data.get("has_readme")),
            "repo_size_bytes": _as_int(
                data.get("repo_size_bytes") or data.get("size_bytes") or data.get("size")),

        }

        card = data.get("cardData")
        if isinstance(card, dict):
            formatted["card_keys"] = sorted(card.keys())[:10]

        return formatted

    def display_data(
        self, formatted_data: Dict[str, Any], raw_data: Dict[str, Any]
    ) -> None:
        typer.echo(json.dumps(formatted_data, indent=2, ensure_ascii=False))
