from _typeshed import Incomplete

DISABLE_PROMPT: Incomplete
EXIT_STATUS: int
BOOL_TRUE_RESPONSES: Incomplete

class PromptExit(RuntimeError): ...

def parseIntList(resp): ...
def prompt(msg, default: Incomplete | None = None, required: bool = True, type_=..., validate: Incomplete | None = None, choices: Incomplete | None = None): ...
