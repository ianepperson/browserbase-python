from unittest.mock import MagicMock
from urllib.parse import urlparse
import pytest
from respx import MockRouter

from browserbase.selenium import Browserbase
from browserbase.selenium.sl_connection import BrowserbaseConnection
from browserbase.selenium.sl_session import SeleniumSession

from browserbase.core import SESSION_WEBDRIVER_URL


@pytest.fixture
def bbase(api_key, project_id) -> Browserbase:
    return Browserbase(api_key=api_key, project_id=project_id)


def test_get_new_sl_session(
    bbase: Browserbase,
    mock_session_response,
    respx_mock: MockRouter,
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

    mock_driver = mocker.patch(
        "browserbase.selenium.sl_connection.Remote",
    )

    with bbase.session() as session:
        assert session.id == session_id

        # Look up the most recent request
        last_request = respx_mock.calls.last.request
        assert last_request.url.path == "/v1/sessions"

        # Ensure that the mocked page object was returned
        assert isinstance(session.driver, MagicMock)

    # Should not have sent the request to end the session
    assert (
        last_request == respx_mock.calls.last.request
    ), "Additional unexpected call made after session close."

    assert mock_driver.call_count == 1
    called_connection = mock_driver.call_args[0][0]
    assert isinstance(called_connection, BrowserbaseConnection)


def test_sl_connection_headers(
    bbase: Browserbase,
    sample_session_response_json: dict,
    api_key: str,
    session_id: str,
):
    """
    Test to see if the remote connection override is working as expected.
    """
    session = SeleniumSession.from_api_response(
        bbase, sample_session_response_json
    )
    url = urlparse(SESSION_WEBDRIVER_URL)
    connection = BrowserbaseConnection(session, url, ignore_proxy=True)
    headers = connection.get_remote_connection_headers(url)

    assert headers["session-id"] == session_id
    assert headers["x-bb-api-key"] == api_key
