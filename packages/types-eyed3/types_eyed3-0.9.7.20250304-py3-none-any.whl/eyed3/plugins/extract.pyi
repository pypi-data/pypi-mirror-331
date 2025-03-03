import eyed3.plugins
from _typeshed import Incomplete

class ExtractPlugin(eyed3.plugins.LoaderPlugin):
    NAMES: Incomplete
    SUMMARY: str
    def __init__(self, arg_parser) -> None: ...
    def handleFile(self, f, *args, **kwargs): ...
