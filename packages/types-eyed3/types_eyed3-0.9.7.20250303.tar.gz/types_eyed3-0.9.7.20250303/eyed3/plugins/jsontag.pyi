import eyed3.plugins
from _typeshed import Incomplete

class JsonTagPlugin(eyed3.plugins.LoaderPlugin):
    NAMES: Incomplete
    SUMMARY: str
    def __init__(self, arg_parser) -> None: ...
    def handleFile(self, f, *args, **kwargs) -> None: ...

def audioFileToJson(audio_file): ...
