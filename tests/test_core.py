import os
from datetime import datetime
from unittest import mock

import httpx
import pytest
from respx import MockRouter

from browserbase import Browserbase
from browserbase.core import ENVIRON_API_KEY, ENVIRON_PROJECT_ID


def test_core_init(api_key: str, project_id: str):
    bbase = Browserbase(api_key=api_key, project_id=project_id)

    assert bbase.project_id == project_id
    assert bbase._api_key == api_key


def test_core_bad_init(api_key: str):
    with pytest.raises(ValueError) as e_info:
        Browserbase(api_key=api_key, project_id="not-a-UUID")

    # Make sure the error message complains about the project_id parameter
    assert "project_id parameter" in e_info.value.args[0]


def test_core_init_from_environ(api_key: str, project_id: str):
    mock_environment = {
        ENVIRON_API_KEY: api_key,
        ENVIRON_PROJECT_ID: project_id,
    }
    with mock.patch.dict(os.environ, mock_environment):
        bbase = Browserbase()

    assert bbase.project_id == project_id
    assert bbase._api_key == api_key


def test_core_init_from_bad_environ(api_key: str):
    mock_environment = {
        ENVIRON_API_KEY: api_key,
        ENVIRON_PROJECT_ID: "not-a-UUID",
    }
    with mock.patch.dict(os.environ, mock_environment):
        with pytest.raises(ValueError) as e_info:
            Browserbase()

    # Make sure the error message complains about an env variable
    assert "environment variable" in e_info.value.args[0]
    assert ENVIRON_PROJECT_ID in e_info.value.args[0]


def test_core_authentication(
    bbase: Browserbase, api_key: str, respx_mock: MockRouter
):
    mock_response = httpx.Response(200, json=[])
    respx_mock.get("https://www.browserbase.com/v1/sessions").mock(
        return_value=mock_response
    )

    # perform a basic action that requires authentication
    bbase.list_sessions()

    # look up the most recent request
    last_request = respx_mock.calls.last.request
    # check to ensure the API key is in the proper header
    assert last_request.headers["x-bb-api-key"] == api_key


def test_core_bad_authentication(
    bbase: Browserbase, api_key: str, respx_mock: MockRouter
):
    mock_response = httpx.Response(403)
    respx_mock.get("https://www.browserbase.com/v1/sessions").mock(
        return_value=mock_response
    )

    with pytest.raises(httpx.HTTPStatusError):
        # perform a basic action that requires authentication
        bbase.list_sessions()


@pytest.mark.parametrize(
    "option, url_param",
    [
        (None, ""),
        ("RUNNING", "?status=RUNNING"),
        ("COMPLETED", "?status=COMPLETED"),
    ],
)
def test_core_list_sessions(
    bbase: Browserbase,
    respx_mock: MockRouter,
    option,
    url_param: str,
    session_id: str,
):
    now = datetime.now()
    timestamp = now.isoformat()
    mock_response = httpx.Response(
        200,
        json=[
            {
                "id": session_id,
                "createdAt": timestamp,
                "startedAt": timestamp,
                "updatedAt": timestamp,
                "status": option or "RUNNING",
                "projectId": bbase.project_id,
            }
        ],
    )
    respx_mock.get("https://www.browserbase.com/v1/sessions" + url_param).mock(
        return_value=mock_response
    )

    sessions = bbase.list_sessions(option)

    assert sessions[0].id == session_id
    assert sessions[0].created_at == now
    assert sessions[0].status == (option or "RUNNING")


@pytest.mark.parametrize(
    "option, url_param",
    [
        (None, ""),
        ("RUNNING", "?status=RUNNING"),
        ("COMPLETED", "?status=COMPLETED"),
    ],
)
@pytest.mark.asyncio
async def test_core_alist_sessions(
    bbase: Browserbase,
    respx_mock: MockRouter,
    option,
    url_param: str,
    session_id: str,
):
    now = datetime(2024, 2, 28, 12, 55, 45, 1000)
    timestamp = now.isoformat()
    mock_response = httpx.Response(
        200,
        json=[
            {
                "id": session_id,
                "createdAt": timestamp,
                "startedAt": timestamp,
                "updatedAt": timestamp,
                "status": option or "RUNNING",
                "projectId": bbase.project_id,
            }
        ],
    )
    respx_mock.get("https://www.browserbase.com/v1/sessions" + url_param).mock(
        return_value=mock_response
    )

    sessions = await bbase.alist_sessions(option)

    assert sessions[0].id == session_id
    assert sessions[0].created_at == now
    assert sessions[0].status == (option or "RUNNING")
