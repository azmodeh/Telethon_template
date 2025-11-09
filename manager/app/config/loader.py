# rootdir: manager/app/config/loader.py
from pathlib import Path
import json

BASE = Path(__file__).parent.parent.parent
DATA = BASE / "data"
TEXT = DATA / "text"
CONFIG = DATA / "config"


def load_json(folder: str, name: str) -> dict:
    """بارگذاری فایل JSON"""
    path = DATA / folder / f"{name}.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# بارگذاری تنظیمات
ENV = load_json("config", "env")
SETTINGS = load_json("config", "settings")

# بارگذاری متن‌ها
MESSAGES = load_json("text", "messages")
ERRORS = load_json("text", "errors")
PATTERNS = load_json("text", "patterns")
QUERIES = load_json("text", "queries")
COMMANDS = load_json("text", "commands")