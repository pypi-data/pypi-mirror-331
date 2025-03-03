import dataclasses
from os import PathLike
from . import LOCAL_FS_ENCODING as LOCAL_FS_ENCODING
from _typeshed import Incomplete
from typing import NamedTuple, TypeAlias

AUDIO_NONE: int
AUDIO_MP3: int
AUDIO_TYPES: tuple[int, int]
LP_TYPE: str
EP_TYPE: str
EP_MAX_SIZE_HINT: int
COMP_TYPE: str
LIVE_TYPE: str
VARIOUS_TYPE: str
DEMO_TYPE: str
SINGLE_TYPE: str
ALBUM_TYPE_IDS: list[str]
VARIOUS_ARTISTS: str
TXXX_ALBUM_TYPE: str
TXXX_ARTIST_ORIGIN: str

class CountAndTotalTuple(NamedTuple):
    count: int # type: ignore
    total: int

@dataclasses.dataclass
class ArtistOrigin:
    city: str
    state: str
    country: str
    def id3Encode(self) -> str: ...
    def __init__(self, city: str, state: str, country: str) -> None: ...

@dataclasses.dataclass
class AudioInfo:
    time_secs: float
    size_bytes: int
    def __init__(self, time_secs: float, size_bytes: int) -> None: ...

class Tag:
    read_only: bool
    artist: str | None
    album_artist: str | None
    album: str | None
    title: str | None
    track_num: CountAndTotalTuple | None
    def __init__(self, title: str | None = None, artist: str | None = None, album: str | None = None, album_artist: str | None = None, track_num: str | None = None) -> None: ...

_VersionTuple: TypeAlias = tuple[int | None, int | None, int | None]

class AudioFile:
    path: str
    def initTag(self, version: _VersionTuple | None = None) -> None: ...
    def rename(self, name: str, fsencoding: str = ..., preserve_file_time: bool = False) -> None: ...
    @property
    def info(self) -> AudioInfo: ...
    @property
    def tag(self) -> Tag: ...
    @tag.setter
    def tag(self, t: Tag) -> None: ...
    type: int
    def __init__(self, path: str | PathLike[str]) -> None: ...

class Date:
    TIME_STAMP_FORMATS: Incomplete
    def __init__(self, year: int, month: Incomplete | None = None, day: Incomplete | None = None, hour: Incomplete | None = None, minute: Incomplete | None = None, second: Incomplete | None = None) -> None: ...
    @property
    def year(self) -> int: ...
    @property
    def month(self) -> int: ...
    @property
    def day(self) -> int: ...
    @property
    def hour(self) -> int: ...
    @property
    def minute(self) -> int: ...
    @property
    def second(self) -> int: ...
    def __eq__(self, rhs: object) -> bool: ...
    def __ne__(self, rhs: object) -> bool: ...
    def __lt__(self, rhs: object) -> bool: ...
    def __hash__(self) -> int: ...
    @staticmethod
    def parse(s: str | bytes) -> "Date": ...

def load(path: str | PathLike[str], tag_version: _VersionTuple | None = None) -> AudioFile | None: ...
