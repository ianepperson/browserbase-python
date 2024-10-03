from datetime import datetime, timezone

import httpx
import pytest

from browserbase import AsyncSession, BaseSession, Browserbase, SyncSession


@pytest.fixture(scope="session")
def api_key() -> str:
    return "mock-api-key-12345"


@pytest.fixture(scope="session")
def project_id() -> str:
    return "11111111-0000-0000-0000-acde00000000"


@pytest.fixture(scope="session")
def session_id() -> str:
    return "22222222-0000-0000-0000-acde00000000"


@pytest.fixture
def bbase(api_key, project_id) -> Browserbase:
    return Browserbase(api_key=api_key, project_id=project_id)


@pytest.fixture
def sample_session_response_json(project_id, session_id):

    now = datetime(2024, 2, 28, 11, 55, 45, 1000, tzinfo=timezone.utc)
    soon = datetime(2024, 2, 28, 12, 15, 45, 1000, tzinfo=timezone.utc)
    timestamp = now.isoformat()
    return {
        "id": session_id,
        "createdAt": timestamp,
        "startedAt": timestamp,
        "updatedAt": timestamp,
        "expiresAt": soon.isoformat(),
        "status": "RUNNING",
        "projectId": project_id,
    }


@pytest.fixture
def mock_session_response(sample_session_response_json):
    json = sample_session_response_json
    return httpx.Response(200, json=json)


@pytest.fixture
def session(bbase, sample_session_response_json):
    return BaseSession.from_api_response(bbase, sample_session_response_json)


@pytest.fixture
def sync_session(bbase, sample_session_response_json):
    return SyncSession.from_api_response(bbase, sample_session_response_json)


@pytest.fixture
def async_session(bbase, sample_session_response_json):
    return AsyncSession.from_api_response(bbase, sample_session_response_json)
