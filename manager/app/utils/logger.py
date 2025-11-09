# rootdir: manager/app/utils/logger.py
import logging
from pathlib import Path
from app.config import DATA

LOGS = DATA / "logs"
LOGS.mkdir(exist_ok=True)


def get_logger(component: str) -> logging.Logger:
    """ساخت logger با فایل جداگانه برای هر کامپوننت"""
    logger = logging.getLogger(component)
    
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        
        fh = logging.FileHandler(
            LOGS / f"{component}.log",
            encoding="utf-8"
        )
        fh.setLevel(logging.DEBUG)
        
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        fmt = logging.Formatter(
            "%(asctime)s|%(name)s|%(levelname)s|%(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        fh.setFormatter(fmt)
        ch.setFormatter(fmt)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
    
    return logger
