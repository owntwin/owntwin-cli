import os
from pathlib import Path

from xdg import xdg_cache_home

CACHE_DIR = None

if os.name == "nt":
    CACHE_DIR = Path(os.path.expandvars("%APPDATA%/owntwin/cache"))
else:
    CACHE_DIR = xdg_cache_home().joinpath("owntwin/")

if not CACHE_DIR.exists():
    CACHE_DIR.mkdir(parents=True)
