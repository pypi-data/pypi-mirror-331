from os import PathLike
from typing import IO, Any

from ..id3.tag import Tag
from .. import Error, core
from _typeshed import Incomplete

log: Incomplete

class Mp3Exception(Error): ...

NAME: str
MIME_TYPES: Incomplete
OTHER_MIME_TYPES: Incomplete
EXTENSIONS: Incomplete

class Mp3AudioInfo(core.AudioInfo):
    mp3_header: Incomplete
    xing_header: Incomplete
    vbri_header: Incomplete
    lame_tag: Incomplete
    bit_rate: Incomplete
    sample_freq: Incomplete
    mode: Incomplete
    def __init__(self, file_obj: IO[Any], start_offset: int, tag: core.Tag) -> None: ...
    @property
    def bit_rate_str(self) -> str: ...

_VersionTuple = tuple[int | None, int | None, int | None]

class Mp3AudioFile(core.AudioFile):
    def __init__(self, path: str | PathLike[str], version: _VersionTuple=...) -> None: ...
    def initTag(self, version: _VersionTuple=...) -> Tag: ... # type: ignore

    @property
    def tag(self) -> Tag | None: ...
    @tag.setter
    def tag(self, t: Tag) -> None: ... # type: ignore
