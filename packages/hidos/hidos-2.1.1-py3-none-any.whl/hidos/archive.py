from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Iterable, Optional, Union
from warnings import warn

from .util import POD
from .dsi import BaseDsi, Dsi, EditionId
from .exceptions import EditionRevisionWarning
from .history import Snapshot, DirectoryRecord, RevisionHistory, RevisionRecord

from sshsig import PublicKey


class Edition:
    def __init__(self, succession: Succession, edid: EditionId):
        self.revision: str | None = None
        self.date: date | None = None
        self.snapshot: Snapshot | None = None
        self.suc = succession
        self.edid = edid
        self.subs: dict[int, Edition] = dict()

    def update(self, dir_rec: DirectoryRecord, revision: str, d: date) -> None:
        ignored = False
        if self.snapshot:
            if dir_rec.obj:
                ignored = dir_rec.obj.hexsha != self.snapshot.hexsha
            else:
                ignored = bool(dir_rec.subs)
        else:
            if dir_rec.subs:
                for num, src in dir_rec.subs.items():
                    if num not in self.subs:
                        self.subs[num] = Edition(self.suc, self.edid.sub(num))
                    self.subs[num].update(src, revision, d)
                if dir_rec.obj:
                    ignored = True
            elif dir_rec.obj:
                if not self.subs:
                    self.snapshot = dir_rec.obj
                    self.revision = revision
                    self.date = d
                else:
                    ignored = True
        if ignored:
            msg = "Ignored digital object for edition {}"
            warn(msg.format(self.edid), EditionRevisionWarning)

    @property
    def dsi(self) -> Dsi:
        return Dsi(self.suc.dsi, self.edid)

    @property
    def obj(self) -> Snapshot | None:
        warn("Use Edition.snapshot instead of Edition.obj", DeprecationWarning)
        return self.snapshot

    @property
    def has_digital_object(self) -> bool:
        warn("Use Edition.snapshot instead of has_digital_object", DeprecationWarning)
        return self.snapshot is not None

    @property
    def hexsha(self) -> str | None:
        return self.snapshot.hexsha if self.snapshot else None

    @property
    def swhid(self) -> Optional[str]:
        if self.snapshot:
            scheme = "swh:1:dir:" if self.is_dir else "swh:1:cnt:"
            return scheme + self.snapshot.hexsha
        return None

    @property
    def unlisted(self) -> bool:
        return self.edid.unlisted

    @property
    def obsolete(self) -> bool:
        latest = self.suc.latest(self.unlisted)
        flow = self.flow_edition()
        if latest and flow:
            return flow.edid < latest.edid
        return False

    @property
    def succession(self) -> Succession:
        return self.suc

    @property
    def is_dir(self) -> bool:
        return self.snapshot.is_dir if self.snapshot else False

    def work_copy(self, dest_path: Path) -> None:
        warn("Use snapshot.copy instead of work_copy", DeprecationWarning)
        if self.snapshot:
            self.snapshot.copy(dest_path)

    def flow_edition(self) -> Optional[Edition]:
        return self.latest_sub(self.edid.unlisted)

    def latest_sub(self, unlisted_ok: bool = False) -> Optional[Edition]:
        if self.snapshot:
            return self
        for subid in reversed(sorted(self.subs.keys())):
            if subid > 0 or unlisted_ok:
                ret = self.subs[subid].latest_sub(unlisted_ok)
                if ret is not None:
                    return ret
        return None

    def next_subedition_number(self) -> int:
        nums = self.subs.keys()
        return 1 if not nums else max(nums) + 1

    def all_subeditions(self) -> list[Edition]:
        ret = []
        for sub in self.subs.values():
            ret.append(sub)
            ret += sub.all_subeditions()
        return ret

    def as_pod(self) -> POD:
        ret: dict[str, POD] = dict()
        ret["edid"] = str(self.edid)
        ret["object_type"] = "dir" if self.is_dir else "cnt"
        ret["object_id"] = self.hexsha
        ret["revision"] = self.revision
        ret["date"] = self.date.isoformat() if self.date else None
        return ret


def revision_chain(tip_rev: RevisionRecord) -> list[RevisionRecord]:
    chain = list()
    rev: Optional[RevisionRecord] = tip_rev
    while rev:
        chain.append(rev)
        if len(rev.parents) > 1:
            msg = "Non-linear succession commit histories not supported."
            raise NotImplementedError(msg)
        rev = rev.parent
    return list(reversed(chain))


class Succession:
    def __init__(self, init_rev: RevisionRecord, tip_rev: RevisionRecord):
        self.hexsha = init_rev.hexsha
        self.tip_rev = tip_rev
        self.root = Edition(self, EditionId())
        self.allowed_keys: Optional[set[PublicKey]] = None
        chain = revision_chain(tip_rev)
        if init_rev != chain[0]:
            msg = "{} is not initial commit for commit history to {}"
            raise ValueError(msg.format(init_rev.hexsha, tip_rev.hexsha))
        for rev in chain:
            self.root.update(rev.dir, rev.hexsha, rev.date)
            if rev.allowed_keys is not None:
                self.allowed_keys = rev.allowed_keys
        self._all_editions = [self.root] + self.root.all_subeditions()

    @property
    def dsi(self) -> BaseDsi:
        """Return Digital Succession Id"""
        return BaseDsi.from_sha1_git(self.hexsha)

    @property
    def revision(self) -> str:
        return self.tip_rev.hexsha

    @property
    def is_signed(self) -> bool:
        return self.allowed_keys is not None

    def get(self, edid: EditionId) -> Edition | None:
        for e in self._all_editions:
            if e.edid == edid:
                return e
        return None

    def latest(self, unlisted_ok: bool = False) -> Optional[Edition]:
        return self.root.latest_sub(unlisted_ok)

    def all_editions(self) -> list[Edition]:
        return self._all_editions

    def all_revisions(self) -> Iterable[RevisionRecord]:
        ret = set()
        todo = {self.tip_rev}
        while todo:
            dothis = todo.pop()
            ret.add(dothis)
            todo.update(dothis.parents)
        return ret

    def as_pod(self) -> POD:
        ret: dict[str, POD] = dict()
        ret["dsi"] = str(self.dsi)
        eds = list()
        for sub in self.root.all_subeditions():
            if sub.snapshot:
                eds.append(sub.as_pod())
        if self.allowed_keys is not None:
            ret["allowed_keys"] = [str(k) for k in self.allowed_keys]
        ret["editions"] = eds
        return ret


def history_successions(history: RevisionHistory) -> set[Succession]:
    ret = set()
    for init in history.genesis_records():
        tip = history.find_tip(init)
        if tip:
            ret.add(Succession(init, tip))
    return ret


class SuccessionArchive:
    def __init__(self, history: RevisionHistory) -> None:
        self.successions = dict()
        for succ in history_successions(history):
            self.successions[succ.dsi] = succ

    def find_succession(self, base_dsi: Union[BaseDsi, str]) -> Optional[Succession]:
        return self.successions.get(BaseDsi(base_dsi))

    def as_pod(self) -> POD:
        ret: dict[str, POD] = dict()
        ret["successions"] = [succ.as_pod() for succ in self.successions.values()]
        return ret
