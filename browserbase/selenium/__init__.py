try:
    from selenium import webdriver as _
except ModuleNotFoundError:
    raise Exception(
        "Selenium not installed. Please install the optional selenium module"
    )

from .sl_browserbase import SeleniumBrowserbase as Browserbase
from .sl_session import SeleniumSession as SyncSession
from .sl_connection import BrowserbaseConnection


__all__ = [
    "Browserbase",
    "SyncSession",
    "BrowserbaseConnection",
]
