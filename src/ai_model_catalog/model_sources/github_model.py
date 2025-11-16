# --- stdlib ---
from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any, Dict

import typer

# --- first-party ---
from .. import fetch_repo as fr

# --- local ---
from ..utils import _as_bool, _as_int
from .base import BaseHandler

log = logging.getLogger(__name__)


@dataclass
class RepositoryHandler(BaseHandler):
    owner: str
    repo: str

    def fetch_data(self) -> Dict[str, Any]:
        log.info("Fetching repo data: %s/%s", self.owner, self.repo)
        data = fr.fetch_repo_data(owner=self.owner, repo=self.repo)
        if not isinstance(data, dict):
            raise TypeError("fetch_repo_data() must return a dict")
        return data

    def format_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # owner may be a dict from GitHub API
        owner_val = data.get("author") or data.get("owner") or ""
        if isinstance(owner_val, dict):
            owner_val = owner_val.get("login") or owner_val.get("name") or ""

        license_val = data.get("license")
        if isinstance(license_val, dict):
            license_val = license_val.get("spdx_id") or license_val.get("key") or ""

        formatted: Dict[str, Any] = {
            "source": "github",
            "full_name": f"{self.owner}/{self.repo}",
            "id": data.get("id") or data.get("name") or f"{self.owner}/{self.repo}",
            "author": owner_val or "",
            "license": license_val or "",
            "downloads": _as_int(data.get("downloads")),  # mock supplies this
            "commits_count": _as_int(data.get("commits_count")),  # mock supplies this
            "last_modified": data.get("last_modified")
            or data.get("pushed_at")
            or data.get("updated_at")
            or "",
            "has_readme": _as_bool(data.get("readme")) or _as_bool(data.get("has_readme")),
            "repo_size_bytes": _as_int(
                data.get("repo_size_bytes") or data.get("size_bytes") or data.get("size")),
        }

        for k in ("description", "topics", "tags", "default_branch"):
            if k in data:
                formatted[k] = data[k]

        return formatted

    def display_data(
        self, formatted_data: Dict[str, Any], raw_data: Dict[str, Any]
    ) -> None:
        # Always output JSON (prevents dict formatting errors)
        typer.echo(json.dumps(formatted_data, indent=2, ensure_ascii=False))
