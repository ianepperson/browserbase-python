from datetime import datetime, timedelta
from logging import getLogger
from typing import TYPE_CHECKING, Optional

from .api_models import SESSIONSTATUS, CreateSessionOptions, SessionResponse

if TYPE_CHECKING:
    from .core import BrowserbaseCore

logger = getLogger("browserbase")
logger.propagate = False  # Don't roll logs up to the root logger

SESSIONS_URL = "https://www.browserbase.com/v1/sessions"


class BaseSession:
    """
    Base class for all Browwserbase Session objects.

    None of the session classes are meant to be used directly,
    but are passed as return values to various actions on the
    core Browserbase class.
    """

    _api_response: Optional[SessionResponse] = None
    _browserbase: "BrowserbaseCore"
    _session_options: CreateSessionOptions
    _enable_proxy: bool

    # Indicates that the client assumes the session has ended
    _implicit_end: bool = False

    def __init__(
        self,
        bbase: "BrowserbaseCore",
        session_options: Optional[CreateSessionOptions] = None,
        enable_proxy: bool = False,
    ):
        self._browserbase = bbase
        self._session_options = session_options or CreateSessionOptions()
        self._session_options.project_id = bbase.project_id
        self._enable_proxy = enable_proxy

    @classmethod
    def from_api_response(cls, bbase: "BrowserbaseCore", response_dict: dict):
        """
        Create a new SyncSession from the response data
        """
        api_response = SessionResponse.model_validate(response_dict)
        session = cls(bbase)
        session._api_response = api_response

        return session

    #
    # Provide pass-through information from the API response
    #

    @property
    def id(self) -> str:
        if not self._api_response:
            return ""
        return self._api_response.id

    @property
    def created_at(self) -> datetime:
        if not self._api_response:
            return datetime.min
        return self._api_response.created_at

    @property
    def started_at(self) -> Optional[datetime]:
        if not self._api_response:
            return None
        return self._api_response.started_at

    @property
    def ended_at(self) -> Optional[datetime]:
        if not self._api_response:
            return None
        return self._api_response.ended_at

    @property
    def duration(self) -> Optional[timedelta]:
        if self.started_at is None or self.ended_at is None:
            return None
        return self.ended_at - self.started_at

    @property
    def expires_at(self) -> Optional[datetime]:
        if not self._api_response:
            return None
        return self._api_response.expires_at

    @property
    def status(self) -> Optional[SESSIONSTATUS]:
        if not self._api_response:
            return None
        return self._api_response.status

    #
    # Better representation
    #

    def __str__(self):
        cls_name = self.__class__.__name__
        return f"<{cls_name}(id={self.id})>"

    def __repr__(self):
        cls_name = self.__class__.__name__
        return f"<{cls_name}(id={self.id})>"

    #
    # Session management utilities
    #

    @property
    def _end_session_options(self) -> CreateSessionOptions:
        """
        Return the options used to close a session.
        """
        return CreateSessionOptions(
            project_id=self._browserbase.project_id, status="REQUEST_RELEASE"
        )

    def _check_expiration(self):
        """
        Check if the local clock indicates the session has expired and set
        the _implicit_end flag if it has.
        """
        # TODO: To account for clock differences, save the local time when the
        # client thinks the request was created, and compare that to the time
        # in the response, then add that adjustment to this calculation.
        if self.expires_at is not None and self.expires_at >= datetime.now():
            self._implicit_end = True

    @property
    def implicit_end(self) -> bool:
        if self._implicit_end:
            return True

        # Check to see if we've reached the end-time of the session
        self._check_expiration()

        return self._implicit_end

    @implicit_end.setter
    def implicit_end(self, value: bool):
        self._implicit_end = value
