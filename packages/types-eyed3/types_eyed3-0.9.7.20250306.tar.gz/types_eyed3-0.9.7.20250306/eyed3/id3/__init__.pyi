from typing import Literal, TypeAlias
from . import frames as frames
from .. import Error, core
from .tag import FileInfo as FileInfo, Tag as Tag, TagException as TagException, TagTemplate as TagTemplate
from collections.abc import Generator

_VersionTuple: TypeAlias = tuple[int | None, int | None, int | None]

ID3_V1: _VersionTuple
ID3_V1_0: _VersionTuple
ID3_V1_1: _VersionTuple
ID3_V2: _VersionTuple
ID3_V2_2: _VersionTuple
ID3_V2_3: _VersionTuple
ID3_V2_4: _VersionTuple
ID3_DEFAULT_VERSION = ID3_V2_4
ID3_ANY_VERSION: _VersionTuple
LATIN1_ENCODING: bytes
UTF_16_ENCODING: bytes
UTF_16BE_ENCODING: bytes
UTF_8_ENCODING: bytes
DEFAULT_LANG: bytes
ID3_MIME_TYPE: str
ID3_MIME_TYPE_EXTENSIONS: tuple[Literal[".id3"], Literal[".tag"]]

def isValidVersion(v: _VersionTuple, fully_qualified: bool = False) -> bool: ...
def normalizeVersion(v: _VersionTuple) -> _VersionTuple: ...
def versionToString(v: _VersionTuple) -> str: ...

class GenreException(Error): ...

class Genre:
    def __init__(self, name: str | None = None, id: int | None = None, genre_map: GenreMap | None = None) -> None: ...
    @property
    def id(self) -> int | None: ...
    @id.setter
    def id(self, val: int | None) -> None: ...
    @property
    def name(self) -> str | None: ...
    @name.setter
    def name(self, val: str | None) -> None: ...
    @staticmethod
    def parse(g_str: str, id3_std: bool = True) -> Genre: ...
    def __eq__(self, rhs: object) -> bool: ...
    def __lt__(self, rhs: object) -> bool: ...

class GenreMap(dict[str | int, int | Genre]):
    GENRE_MIN: int
    GENRE_MAX: None
    ID3_GENRE_MIN: int
    ID3_GENRE_MAX: int
    WINAMP_GENRE_MIN: int
    WINAMP_GENRE_MAX: int
    GENRE_ID3V1_MAX: int
    def get(self, key: int | str) -> Genre: ... # type: ignore
    def __getitem__(self, key: int | str) -> Genre: ...
    @property
    def ids(self) -> list[int]: ...
    def iter(self) -> Generator[Genre]: ...

class TagFile(core.AudioFile):
    ...

ID3_GENRES: list[str]
genres: GenreMap
