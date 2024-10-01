from datetime import datetime

from browserbase import BaseSession, Browserbase


def test_blank_session(bbase: Browserbase):
    """
    Check the properties when there is no data in the session.
    """
    new_session = BaseSession(bbase)

    assert new_session.id == ""
    assert new_session.created_at == datetime.min
    assert new_session.started_at is None
    assert new_session.ended_at is None
    assert new_session.expires_at is None
    assert new_session.status is None
    assert new_session.duration is None


def test_returned_session(session, session_id: str):
    """
    Check the properties when there is data in the session.
    """

    assert session.id == session_id
    assert session.created_at.year == 2024
    assert session.started_at is not None
    assert session.started_at.year == 2024
    assert session.ended_at is None
    assert session.expires_at is not None
    assert session.expires_at.year == 2024
    assert session.status == "RUNNING"


def test_session_duration(bbase: Browserbase, sample_session_response_json):
    """
    Check the properties when there is data in the session.
    """
    end_time = sample_session_response_json["expiresAt"]
    sample_session_response_json["endedAt"] = end_time

    new_session = BaseSession.from_api_response(
        bbase, sample_session_response_json
    )

    assert new_session.ended_at is not None
    assert new_session.ended_at.hour == 12
    assert new_session.duration is not None
    assert new_session.duration.total_seconds() == 1200
