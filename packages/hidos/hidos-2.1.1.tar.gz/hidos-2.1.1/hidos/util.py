import dataclasses, logging
from warnings import warn
from pathlib import Path
from typing import Any, Iterable, Mapping, TextIO, Union, cast

from sshsig import PublicKey

from .dsi import BaseDsi


LOG = logging.getLogger('hidos')

# git hash-object -t tree /dev/null
EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"

JSONType = Union[None, str, int, float, list['JSONType'], dict[str, 'JSONType']]


def JSON_list(value: JSONType) -> list[JSONType]:
    return value if isinstance(value, list) else []


def JSON_get_list(d: JSONType, key: str) -> list[JSONType]:
    return JSON_list(d.get(key) if isinstance(d, dict) else [])


def JSON_dict(value: JSONType) -> dict[str, JSONType]:
    return value if isinstance(value, dict) else {}


def JSON_get_dict(d: JSONType, key: str) -> dict[str, JSONType]:
    return JSON_dict(d.get(key) if isinstance(d, dict) else {})


def JSON_get_str(d: JSONType, key: str, *subkeys: str) -> str:
    value = d.get(key) if isinstance(d, dict) else ""
    if len(subkeys):
        return JSON_get_str(value, *subkeys)
    return value if isinstance(value, str) else ""


# Persistable/Plain-Old-Data type, a subset of JSON data.
# No float due to rounding errors of float (de)serialization.
POD = Union[None, str, int, list['POD'], dict[str, 'POD']]


def PODify(x: Any) -> POD:
    if hasattr(x, 'as_pod'):
        return cast(POD, x.as_pod())
    if isinstance(x, (type(None), str, int, list, dict)):
        return x
    if isinstance(x, Iterable):
        return [PODify(e) for e in x]
    if isinstance(x, Mapping):
        ret: dict[str, POD] = dict()
        for k, v in x.items():
            if not isinstance(k, str):
                raise ValueError
            ret[k] = PODify(v)
        return ret
    if dataclasses.is_dataclass(x) and not isinstance(x, type):
        return list(dataclasses.astuple(x))
    raise ValueError


def b64url_from_sha1(hexstr: str) -> str:
    warn("Use BaseDsi instead of b64url_from_sha1", DeprecationWarning)
    return str(BaseDsi.from_sha1_git(hexstr))


def sha1_from_b64url(b64url: str) -> str:
    warn("Use BaseDsi instead of sha1_from_b64url", DeprecationWarning)
    return BaseDsi(b64url).sha1_git


def load_openssh_public_key_file(file: Union[Path, TextIO]) -> set[PublicKey]:
    """Read public key file in "OpenSSH format".

    Multiple lines are read as a concatenation of multiple OpenSSH format files.
    """
    if isinstance(file, Path):
        with open(file, encoding="ascii") as f:
            return load_openssh_public_key_file(f)
    ret = set()
    for line in file.readlines():
        ret.add(PublicKey.from_openssh_str(line))
    return ret
