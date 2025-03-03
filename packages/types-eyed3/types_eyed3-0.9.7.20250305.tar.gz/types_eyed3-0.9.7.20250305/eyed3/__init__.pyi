from typing import Any
from .__about__ import __version__ as version
from .core import AudioFile as AudioFile, load as load

__all__ = ['AudioFile', 'load', 'version', 'LOCAL_ENCODING', 'LOCAL_FS_ENCODING', 'Error']

LOCAL_ENCODING: str
LOCAL_FS_ENCODING: str

class Error(Exception):
    """Base exception type for all eyed3 errors."""
    message: Any
    def __init__(self, *args: tuple[Any, ...]) -> None: ...
