# App command interface, juse a prue Python shell.
from .pypysh import main

__doc__ = pypysh.__doc__
if hasattr(pypysh, "__all__"):
    __all__ = pypysh.__all__