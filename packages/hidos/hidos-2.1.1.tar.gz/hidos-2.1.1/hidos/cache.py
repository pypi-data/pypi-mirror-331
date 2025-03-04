from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

from platformdirs import user_cache_path
from requests_cache import CachedSession

from .archive import Succession, history_successions
from .dsi import BaseDsi, EditionId
from .dulwich import DulwichBackend
from .remote import FederatedClient, RemoteBranchId
from .history import RevisionHistory


class SuccessionDataMissing(Exception):
    pass


class SuccessionCache:
    def __init__(self, cache_root: Path | None = None, offline: bool = False):
        self.cache_root = cache_root or user_cache_path("hidos", ensure_exists=True)
        self.offline = offline
        http_cache = CachedSession(
            self.cache_root / "http",
            allowable_codes=(200, 404),
            cache_control=True,
            stale_if_error=offline,
        )
        self._client = FederatedClient(http_cache, offline=offline)

    def clear(self) -> None:
        shutil.rmtree(self.cache_root)

    def lookup_remote_branches(self, dsi: BaseDsi) ->  set[RemoteBranchId]:
        return self._client.lookup_remote_branches(dsi)

    def get(self, dsi: BaseDsi) -> Succession:
        if not isinstance(dsi, BaseDsi):
            dsi = BaseDsi(dsi)
        subcache = self.cache_root / dsi.base64
        if subcache.exists():
            repo = DulwichBackend.read_repo(subcache)
        elif self.offline:
            raise SuccessionDataMissing(dsi)
        else:
            repo = DulwichBackend.init_bare_repo(subcache)
        if not self.offline:
            for branch in self._client.lookup_remote_branches(dsi):
                repo.fetch(branch.origin, branch.name)
        for succ in history_successions(RevisionHistory(repo.tips())):
            if succ.dsi == dsi:
               return succ
        raise SuccessionDataMissing(dsi)

    def archive_dates(self, succ: Succession) -> dict[EditionId, datetime | None]:
        return self._client.edition_archive_dates(succ)
