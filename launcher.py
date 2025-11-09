# rootdir/launcher.py
# ======================================================
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.core.application import start

if __name__ == "__main__":
    start()