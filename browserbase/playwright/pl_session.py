from typing import Generic, Optional, TypeVar

from playwright.async_api import Page as AsyncPage
from playwright.sync_api import Page as SyncPage

from ..async_session import AsyncSession
from ..sync_session import SyncSession

P = TypeVar("P", SyncPage, AsyncPage)


class PlaywrightSessionMixin(Generic[P]):
    _page: Optional[P] = None

    @property
    def page(self) -> P:
        if self._page is None:
            raise RuntimeError("session.page has not been set.")
        return self._page

    @page.setter
    def page(self, new_page: P):
        if self._page is not None:
            raise RuntimeError("Attempt to reassign session.page")
        self._page = new_page


class PlaywrightSyncSession(SyncSession, PlaywrightSessionMixin[SyncPage]):
    SyncSession.__doc__


class PlaywrightAsyncSession(AsyncSession, PlaywrightSessionMixin[AsyncPage]):
    AsyncSession.__doc__
