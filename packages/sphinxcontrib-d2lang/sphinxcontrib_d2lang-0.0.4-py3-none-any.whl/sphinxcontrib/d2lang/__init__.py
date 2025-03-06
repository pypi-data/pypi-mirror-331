try:
    from sphinx.application import Sphinx
except:
    pass

from .d2lang import D2langDirective

from typing import Any, Dict, List, Tuple

from shutil import which

__version__ = (0, 0, 1)

def setup(application: Sphinx) -> Dict[str, Any]:
    """
    setup extension.
    """
    if which('d2'):
        application.add_directive('d2lang', D2langDirective)
        return {"version": __version__, "parallel_read_safe": True}
    else:
        print("d2 binary not found in $PATH")
        raise
