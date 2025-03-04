from pathlib import Path
import sys
import os


def get_version_number():
    try:
        dir_path = str(Path(os.path.dirname(__file__)).parent)
        sys.path.append(dir_path)

        from versions import get_latest_number
        version = get_latest_number()
    except ImportError:
        from .__init__ import __version__
        version = __version__

    return version
