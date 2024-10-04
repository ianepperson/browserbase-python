"""
Implement the basic Browserbase object to be used for interacting with
the Browserbase service.

Provides a concrete implementation of the session and asession
context managers.
"""

from typing import AsyncContextManager, ContextManager, Optional

from .api_models import CreateSessionOptions, Fingerprint, Viewport
from .async_session import AsyncSession
from .core import BrowserbaseCore
from .sync_session import SyncSession


class Browserbase(BrowserbaseCore[SyncSession, AsyncSession]):
    def session(
        self,
        timeout: Optional[int] = None,
        extension_id: Optional[str] = None,
        keep_alive: Optional[bool] = None,
        fingerprint: Optional[Fingerprint] = None,
        viewport: Optional[Viewport] = None,
        enable_proxy: bool = False,
    ) -> ContextManager[SyncSession]:

        options = CreateSessionOptions(
            timeout=timeout,
            extension_id=extension_id,
            keep_alive=keep_alive,
            fingerprint=fingerprint,
            viewport=viewport,
        )

        new_session = SyncSession(self, options, enable_proxy=enable_proxy)
        return self._session_manager(new_session)

    def asession(
        self,
        timeout: Optional[int] = None,
        extension_id: Optional[str] = None,
        keep_alive: Optional[bool] = None,
        fingerprint: Optional[Fingerprint] = None,
        viewport: Optional[Viewport] = None,
        enable_proxy: bool = False,
    ) -> AsyncContextManager[AsyncSession]:

        options = CreateSessionOptions(
            timeout=timeout,
            extension_id=extension_id,
            keep_alive=keep_alive,
            fingerprint=fingerprint,
            viewport=viewport,
        )

        new_session = AsyncSession(self, options, enable_proxy=enable_proxy)
        return self._asession_manager(new_session)
