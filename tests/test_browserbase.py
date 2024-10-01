import json

import pytest
from respx import MockRouter

from browserbase import Browserbase


def test_get_new_session(
    bbase: Browserbase,
    mock_session_response,
    respx_mock: MockRouter,
    session_id: str,
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

    with bbase.session() as session:
        assert session.id == session_id

        # Look up the most recent request
        last_request = respx_mock.calls.last.request
        assert last_request.url.path == "/v1/sessions"

    # Should have sent the request to end the session
    # Look up the most recent request
    last_request = respx_mock.calls.last.request
    # check to ensure the session was requested to close
    assert last_request.url.path == f"/v1/sessions/{session_id}"
    assert json.loads(last_request.content) == {
        "status": "REQUEST_RELEASE",
        "projectId": bbase.project_id,
    }


@pytest.mark.asyncio
async def test_get_new_asession(
    bbase: Browserbase,
    mock_session_response,
    respx_mock: MockRouter,
    session_id: str,
):
    """
    Ensure the session async context block is doing the right thing.
    """
    respx_mock.post("https://www.browserbase.com/v1/sessions").mock(
        return_value=mock_session_response
    )
    respx_mock.post(
        f"https://www.browserbase.com/v1/sessions/{session_id}"
    ).mock(return_value=mock_session_response)

    async with bbase.asession() as session:
        assert session.id == session_id

        # Look up the most recent request
        last_request = respx_mock.calls.last.request
        assert last_request.url.path == "/v1/sessions"

    # Should have sent the request to end the session
    # Look up the most recent request
    last_request = respx_mock.calls.last.request
    # check to ensure the session was requested to close
    assert last_request.url.path == f"/v1/sessions/{session_id}"
    assert json.loads(last_request.content) == {
        "status": "REQUEST_RELEASE",
        "projectId": bbase.project_id,
    }
