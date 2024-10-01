from contextlib import asynccontextmanager, contextmanager
from typing import AsyncGenerator, Generator, Optional

from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright

from ..api_models import CreateSessionOptions, Fingerprint, Viewport
from ..core import BrowserbaseCore
from .pl_session import PlaywrightAsyncSession, PlaywrightSyncSession


class PlaywrightBrowserbase(
    BrowserbaseCore[PlaywrightSyncSession, PlaywrightAsyncSession]
):
    # Core connection, with playwright additions.

    @contextmanager
    def session(
        self,
        timeout: Optional[int] = None,
        extension_id: Optional[str] = None,
        keep_alive: Optional[bool] = None,
        fingerprint: Optional[Fingerprint] = None,
        viewport: Optional[Viewport] = None,
        enable_proxy: bool = False,
    ) -> Generator[PlaywrightSyncSession, None, None]:
        # Create sessions with a page property, all connected and ready to use.

        options = CreateSessionOptions(
            timeout=timeout,
            extension_id=extension_id,
            keep_alive=keep_alive,
            fingerprint=fingerprint,
            viewport=viewport,
        )

        new_session = PlaywrightSyncSession(
            self, options, enable_proxy=enable_proxy
        )
        with self._session_manager(
            new_session
        ) as session, sync_playwright() as playwright:
            cdp_url = self.get_cdp_url(session)

            # Connect the playwright instance to the remote browser.
            browser = playwright.chromium.connect_over_cdp(cdp_url)
            try:
                context = browser.contexts[0]
                page = context.pages[0]

                # Set the page within the new session
                session.page = page

                yield session
            finally:
                # Closing the Playwright session will normally end the
                # session.
                session.implicit_end = True

    @asynccontextmanager
    async def asession(
        self,
        timeout: Optional[int] = None,
        extension_id: Optional[str] = None,
        keep_alive: Optional[bool] = None,
        fingerprint: Optional[Fingerprint] = None,
        viewport: Optional[Viewport] = None,
        enable_proxy: bool = False,
    ) -> AsyncGenerator[PlaywrightAsyncSession, None]:
        # Create asessions with a page property, all connected and ready to use.

        options = CreateSessionOptions(
            timeout=timeout,
            extension_id=extension_id,
            keep_alive=keep_alive,
            fingerprint=fingerprint,
            viewport=viewport,
        )

        new_session = PlaywrightAsyncSession(
            self, options, enable_proxy=enable_proxy
        )

        async with self._asession_manager(
            new_session
        ) as session, async_playwright() as playwright:
            cdp_url = self.get_cdp_url(new_session)

            # Connect the playwright instance to the remote browser.
            browser = await playwright.chromium.connect_over_cdp(cdp_url)

            try:
                context = browser.contexts[0]
                page = context.pages[0]
                session.page = page

                yield session
            finally:
                # Closing the Playwright session will normally end the
                # session.
                session.implicit_end = True

    @contextmanager
    def page(self, enable_proxy: bool = False):
        """
        A context manager for opening a single page with an implicit session.

        Note that no session ID (and therefore no session object) is available.
        """
        if enable_proxy:
            cdp_url = self.get_cdp_url(enable_proxy="true")
        else:
            cdp_url = self.get_cdp_url()
        with sync_playwright() as playwright:
            browser = playwright.chromium.connect_over_cdp(cdp_url)

            context = browser.contexts[0]
            page = context.pages[0]

            yield page

    @asynccontextmanager
    async def apage(self, enable_proxy: bool = False):
        """
        A context manager for opening a single page with an explicit session.

        Note that no session ID (and therefore no session object) is available.
        """
        if enable_proxy:
            cdp_url = self.get_cdp_url(enable_proxy="true")
        else:
            cdp_url = self.get_cdp_url()
        async with async_playwright() as playwright:
            browser = await playwright.chromium.connect_over_cdp(cdp_url)

            context = browser.contexts[0]
            page = context.pages[0]

            yield page
