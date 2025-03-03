import dataclasses

__all__ = ['Version', 'project_name', 'version', 'version_info', 'release_name', 'author', 'author_email', 'years', 'description', 'homepage']

@dataclasses.dataclass
class Version:
    major: int
    minor: int
    maint: int
    release: str
    release_name: str
    def __init__(self, major: int, minor: int, maint: int, release: str, release_name: str) -> None: ...

project_name: str
version: str
release_name: str
author: str
author_email: str
years: str
version_info: Version
description: str
homepage: str
