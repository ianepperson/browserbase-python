from contextlib import asynccontextmanager, contextmanager

import pytest
from mock import MagicMock, AsyncMock
from playwright.async_api import Browser, Playwright as SyncPlaywright
from playwright.sync_api import Playwright as AsyncPlaywright
from respx import MockRouter

from browserbase.playwright import Browserbase


class PlaywrightMock:
    """
    Class for mocking playwright sync and async context managers.

    >>> with playwright.sync() as playwright:
            playwright.do_stuff()
    >>> assert playwright.sync_mock.do_stuff.called

    >>> async with playwright.async() as playwright:
            await playwright.do_stuff()
    >>> assert playwright.async_mock.do_stuff.called
    """

    # This is a complex library to Mock out.

    def __init__(self):
        self.sync_mock = MagicMock(spec=SyncPlaywright)
        self._async_mock = MagicMock(spec=AsyncPlaywright)

    @property
    def async_mock(self):
        # Only instantiate the async methods when accessed to prevent
        # creating async objects that don't get awaited.
        self.async_browser = MagicMock(spec=Browser)
        connect_cdp = AsyncMock(return_value=self.async_browser)
        self._async_mock.chromium.connect_over_cdp.side_effect = connect_cdp

        self.async_page = self.async_browser.contexts[0].pages[0]
        return self._async_mock

    @contextmanager
    def sync(self):
        yield self.sync_mock

    @asynccontextmanager
    async def async_(self):
        yield self.async_mock


@pytest.fixture
def playwright():
    """
    Provide the PlaywrightMock via the playwright parameter.
    """

    return PlaywrightMock()


@pytest.fixture
def bbase(api_key, project_id) -> Browserbase:
    return Browserbase(api_key=api_key, project_id=project_id)


def test_get_new_pl_session(
    bbase: Browserbase,
    mock_session_response,
    respx_mock: MockRouter,
    playwright: PlaywrightMock,
    api_key: str,
    session_id: str,
    mocker,
):
    """
    Ensure the session context block is doing the right thing.
    """
    respx_mock.post("https://www.browserbase.com/v1/sessions").mock(
        return_value=mock_session_response
    )
    respx_mock.post(
        f"https://www.browserbase.com/v1/sessions/{session_id}"
    ).mock(return_value=mock_session_response)

    mock_sync_playwright = mocker.patch(
        "browserbase.playwright.pl_browserbase.sync_playwright",
    )
    mock_sync_playwright.return_value = playwright.sync()

    with bbase.session() as session:
        assert session.id == session_id

        # Look up the most recent request
        last_request = respx_mock.calls.last.request
        assert last_request.url.path == "/v1/sessions"

        # Ensure that the mocked page object was returned
        assert isinstance(session.page, MagicMock)

    # Should not have sent the request to end the session
    assert (
        last_request == respx_mock.calls.last.request
    ), "Additional unexpected call made after session close."

    # The playwright session manager should have been called
    assert (
        playwright.sync_mock.chromium.connect_over_cdp.call_args.args[0]
        == f"wss://www.browserbase.com?apiKey={api_key}&sessionId={session_id}"
    )


@pytest.mark.asyncio
async def test_get_new_pl_asession(
    bbase: Browserbase,
    mock_session_response,
    respx_mock: MockRouter,
    playwright: PlaywrightMock,
    api_key: str,
    session_id: str,
    mocker,
):
    """
    Ensure the session context block is doing the right thing.
    """
    respx_mock.post("https://www.browserbase.com/v1/sessions").mock(
        return_value=mock_session_response
    )
    respx_mock.post(
        f"https://www.browserbase.com/v1/sessions/{session_id}"
    ).mock(return_value=mock_session_response)

    mock_async_playwright = mocker.patch(
        "browserbase.playwright.pl_browserbase.async_playwright",
    )
    mock_async_playwright.return_value = playwright.async_()

    async with bbase.asession() as session:
        assert session.id == session_id

        # Look up the most recent request
        last_request = respx_mock.calls.last.request
        assert last_request.url.path == "/v1/sessions"

        # Ensure that the mocked page object was returned
        assert session.page is playwright.async_page

    # Should not have sent the request to end the session
    assert (
        last_request == respx_mock.calls.last.request
    ), "Additional unexpected call made after session close."

    # The playwright connect should have been called
    assert playwright.async_mock.chromium.connect_over_cdp.called
    assert (
        playwright.async_mock.chromium.connect_over_cdp.call_args[0][0]
        == f"wss://www.browserbase.com?apiKey={api_key}&sessionId={session_id}"
    )


def test_get_pl_page(
    bbase: Browserbase,
    playwright: PlaywrightMock,
    api_key: str,
    mocker,
):
    """
    Ensure the page context block is doing the right thing.
    """

    mock_sync_playwright = mocker.patch(
        "browserbase.playwright.pl_browserbase.sync_playwright",
    )
    mock_sync_playwright.return_value = playwright.sync()

    with bbase.page() as page:
        # Ensure that the mocked page object was returned
        assert isinstance(page, MagicMock)

    # The playwright session manager should have been called
    assert (
        playwright.sync_mock.chromium.connect_over_cdp.call_args.args[0]
        == f"wss://www.browserbase.com?apiKey={api_key}"
    )


@pytest.mark.asyncio
async def test_get_pl_apage(
    bbase: Browserbase,
    playwright: PlaywrightMock,
    api_key: str,
    mocker,
):
    """
    Ensure the page context block is doing the right thing.
    """
    mock_async_playwright = mocker.patch(
        "browserbase.playwright.pl_browserbase.async_playwright",
    )
    mock_async_playwright.return_value = playwright.async_()

    async with bbase.apage() as page:
        # Ensure that the mocked page object was returned
        assert page is playwright.async_page

    # The playwright browser should have been called with await
    assert playwright.async_mock.chromium.connect_over_cdp.called
    assert (
        playwright.async_mock.chromium.connect_over_cdp.call_args[0][0]
        == f"wss://www.browserbase.com?apiKey={api_key}"
    )
