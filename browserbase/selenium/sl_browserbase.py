from contextlib import contextmanager
from typing import Generator, Optional

from ..api_models import CreateSessionOptions, Fingerprint, Viewport
from ..async_session import AsyncSession
from ..core import SESSION_WEBDRIVER_URL, BrowserbaseCore
from .sl_connection import BrowserbaseConnection
from .sl_session import SeleniumSession


class SeleniumBrowserbase(BrowserbaseCore[SeleniumSession, AsyncSession]):
    # Core connection, with Selenium additions.

    @contextmanager
    def session(
        self,
        timeout: Optional[int] = None,
        extension_id: Optional[str] = None,
        keep_alive: Optional[bool] = None,
        fingerprint: Optional[Fingerprint] = None,
        viewport: Optional[Viewport] = None,
        enable_proxy: bool = False,
    ) -> Generator[SeleniumSession, None, None]:
        # Create sessions with a driver property, all connected and ready to use.

        options = CreateSessionOptions(
            timeout=timeout,
            extension_id=extension_id,
            keep_alive=keep_alive,
            fingerprint=fingerprint,
            viewport=viewport,
        )

        new_session = SeleniumSession(self, options, enable_proxy=enable_proxy)

        with self._session_manager(new_session) as session:
            # Connect the Selenium driver to the remote session
            connection = BrowserbaseConnection(session, SESSION_WEBDRIVER_URL)
            driver = connection.get_driver()

            session.driver = driver

            try:
                yield session
            finally:
                # Closing the Selenium session will normally end the
                # session.
                session.implicit_end = True

    async def asession(self, *_, **__):
        raise NotImplementedError("The Selenium driver does not support async")
