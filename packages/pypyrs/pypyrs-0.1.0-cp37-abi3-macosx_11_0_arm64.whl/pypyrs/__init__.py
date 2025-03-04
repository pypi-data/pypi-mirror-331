# App command interface, juse a prue Python shell.
from .pypyrs import main

__doc__ = pypyrs.__doc__
if hasattr(pypyrs, "__all__"):
    __all__ = pypyrs.__all__