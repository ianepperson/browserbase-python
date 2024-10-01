import io

import httpx
from respx import MockRouter

from browserbase import SyncSession


def test_get_downloads(
    sync_session: SyncSession,
    session_id: str,
    respx_mock: MockRouter,
):
    response = httpx.Response(200, content="zipfile-content")
    respx_mock.get(
        f"https://www.browserbase.com/v1/sessions/{session_id}/downloads"
    ).mock(return_value=response)
    faux_file = io.BytesIO()

    # Send the downloaded "zip" file to the faux_file buffer
    sync_session.get_zipped_downloads(faux_file)

    assert faux_file.getvalue() == b"zipfile-content"


def test_get_live_urls(
    sync_session: SyncSession,
    session_id: str,
    respx_mock: MockRouter,
):
    debug_urls = {
        "debuggerUrl": "https://debugger-url/",
    }
    response = httpx.Response(200, json=debug_urls)
    respx_mock.get(
        f"https://www.browserbase.com/v1/sessions/{session_id}/debug"
    ).mock(return_value=response)

    # Get the live URLs to connect to a live session
    urls = sync_session.get_live_urls()

    assert urls.debugger_url == "https://debugger-url/"


def test_get_logs(
    sync_session: SyncSession,
    session_id: str,
    respx_mock: MockRouter,
):
    logs_json = [
        {"id": session_id, "method": "GET", "page_id": "1a"},
        {"id": session_id, "method": "POST", "page_id": "2b"},
    ]
    response = httpx.Response(200, json=logs_json)
    respx_mock.get(
        f"https://www.browserbase.com/v1/sessions/{session_id}/logs"
    ).mock(return_value=response)

    # Get the list of log objects
    logs = sync_session.get_logs()

    assert len(logs) == 2
    assert logs[0].id == session_id
    assert logs[0].page_id == "1a"
    assert logs[1].page_id == "2b"


def test_get_recording(
    sync_session: SyncSession,
    session_id: str,
    respx_mock: MockRouter,
):
    recording_json = [
        {"type": "first", "data": {"foo": "bar"}},
        {"type": "last"},
    ]
    response = httpx.Response(200, json=recording_json)
    respx_mock.get(
        f"https://www.browserbase.com/v1/sessions/{session_id}/recording"
    ).mock(return_value=response)

    # Get the list of the recording objects
    recordings = sync_session.get_recording()

    assert len(recordings) == 2
    assert recordings[0].type == "first"
    assert recordings[0].data == {"foo": "bar"}
    assert recordings[1].type == "last"
