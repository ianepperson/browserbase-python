try:
    import playwright as _
except ModuleNotFoundError:
    raise Exception(
        "Playwright not installed. Please install the optional playwright module"
    )

from .pl_browserbase import PlaywrightBrowserbase as Browserbase
from .pl_session import (
    PlaywrightAsyncSession as AsyncSession,
    PlaywrightSyncSession as SyncSession,
)


__all__ = [
    "Browserbase",
    "AsyncSession",
    "SyncSession",
]
