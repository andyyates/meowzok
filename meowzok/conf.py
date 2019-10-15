
#this file copied from meld

import os
import sys
from pathlib import Path

__package__ = "meowzok"
__version__ = "3.21.0"

APPLICATION_ID = "uk.co.schmindie.meowzok"
#RESOURCE_BASE = '?'

# START; these paths are clobbered on install by meowzok.build_helpers
DATADIR = Path(sys.prefix) / "share" / "meowzok"
LOCALEDIR = Path(sys.prefix) / "share" / "locale"
# END

# Flag enabling some workarounds if data dir isn't installed in standard prefix
DATADIR_IS_UNINSTALLED = False
PYTHON_REQUIREMENT_TUPLE = (3, 6)


# Installed from main script
def no_translation(gettext_string: str) -> str:
    return gettext_string


_ = no_translation
ngettext = no_translation


def frozen():
    global DATADIR, LOCALEDIR, DATADIR_IS_UNINSTALLED

    meowzokdir = os.path.dirname(sys.executable)

    DATADIR = os.path.join(meowzokdir, "share", "meowzok")
    LOCALEDIR = os.path.join(meowzokdir, "share", "mo")
    DATADIR_IS_UNINSTALLED = True


def uninstalled():
    global DATADIR, LOCALEDIR, DATADIR_IS_UNINSTALLED

    meowzokdir = Path(__file__).resolve().parent.parent

    DATADIR = meowzokdir / "data"
    LOCALEDIR = meowzokdir / "build" / "mo"
    DATADIR_IS_UNINSTALLED = True

    resource_path = meowzokdir / "meowzok" / "resources"
