"""
Core logic for all "Browserbase" classes.

Uses a required generic ST and AT which represent the return values
for the session() and asession() context managers.

Derived classes are generally limited to defining the session and asession
logic, and all other logic is defined here - including validating
the appropriate API key, Project ID and other shared utilities.
"""

import abc
import os
from contextlib import asynccontextmanager, contextmanager
from typing import (
    AsyncContextManager,
    ContextManager,
    Generic,
    Optional,
    Tuple,
    TypeVar,
)
from urllib.parse import urlencode
from uuid import UUID

import httpx
from httpx import Headers

from .api_models import SESSIONSTATUS, Fingerprint, Viewport
from .async_session import AsyncSession
from .base_session import SESSIONS_API_URL, BaseSession
from .sync_session import SyncSession

ENVIRON_API_KEY = "BROWSERBASE_API_KEY"
ENVIRON_PROJECT_ID = "BROWSERBASE_PROJECT_ID"

SESSION_CDP_URL = "wss://connect.browserbase.com"
SESSION_WEBDRIVER_URL = "http://connect.browserbase.com/webdriver"


ST = TypeVar("ST", bound=SyncSession)
AT = TypeVar("AT", bound=AsyncSession)


class BrowserbaseCore(abc.ABC, Generic[ST, AT]):
    """
    Object to represent a connection to the Browserbase service.

    If the api_key and project_id aren't passed as parameters,
    they'll be looked up from the environment variables.
    BROWSERBASE_API_KEY and BROWSERBASE_PROJECT_ID
    """

    _api_key: str
    _project_id: str

    def __init__(
        self, api_key: Optional[str] = None, project_id: Optional[str] = None
    ):
        self._api_key, self._project_id = self._get_the_settings(
            api_key, project_id
        )

    @classmethod
    def _get_the_settings(
        cls, api_key: Optional[str], project_id: Optional[str]
    ) -> Tuple[str, str]:
        """
        Find and check the API key and project ID.
        """
        api_key = api_key or os.environ.get(ENVIRON_API_KEY)
        if not api_key:
            raise ValueError(
                "The Browserbase API key was not passed to the Browserbase "
                f"init, nor could it be found in the {ENVIRON_API_KEY} "
                "environment variable."
            )

        if project_id:
            try:
                # Validate that the it's a proper UUID
                UUID(project_id)
            except ValueError:
                raise ValueError(
                    "The UUID from the project_id parameter is invalid."
                )
            return api_key, project_id

        project_id = os.environ.get(ENVIRON_PROJECT_ID)

        if not project_id:
            raise ValueError(
                "The Browserbase project ID was not passed to the Browserbase "
                f"init, nor could it be found in the {ENVIRON_PROJECT_ID} "
                "environment variable."
            )
        try:
            # Validate that the it's a proper UUID
            UUID(project_id)
        except ValueError:
            raise ValueError(
                f"The UUID from the {ENVIRON_PROJECT_ID} environment variable is invalid."
            )

        return api_key, project_id

    @property
    def project_id(self) -> str:
        if self._project_id is None:
            raise ValueError("No project ID configured")
        return self._project_id

    #
    # Better representation of the object
    #

    def __str__(self):
        cls_name = self.__class__.__name__
        return f"<{cls_name}(project_id={self.project_id})>"

    def __repr__(self):
        cls_name = self.__class__.__name__
        return f"<{cls_name}(project_id={self.project_id})>"

    #
    # Session management
    #

    @contextmanager
    def _session_manager(self, session: ST):
        """
        Manage a Browserbase sync session
        """
        session.start()
        try:
            yield session
        finally:
            # If the session has not already ended implicitly,
            # end the session.
            if not session.implicit_end:
                session.end()

    @asynccontextmanager
    async def _asession_manager(self, session: AT):
        """
        Manage a Browserbase async session
        """
        await session.start()
        try:
            yield session
        finally:
            # If the session has not already ended implicitly,
            # end the session.
            if not session.implicit_end:
                await session.end()

    @abc.abstractmethod
    def session(
        self,
        timeout: Optional[int] = None,
        extension_id: Optional[str] = None,
        keep_alive: Optional[bool] = None,
        fingerprint: Optional[Fingerprint] = None,
        viewport: Optional[Viewport] = None,
        enable_proxy: bool = False,
    ) -> ContextManager[SyncSession]:
        """
        Open a Browserbase session and provide access to actions on that
        session. The session will close automatically once the block is exited.

        >>> with bbase.session() as session:
                print(session.id)
        """
        # A derived class will create the session from the given options,
        # then use the _session_manager to create the context manager.

    @abc.abstractmethod
    async def asession(
        self,
        timeout: Optional[int] = None,
        extension_id: Optional[str] = None,
        keep_alive: Optional[bool] = None,
        fingerprint: Optional[Fingerprint] = None,
        viewport: Optional[Viewport] = None,
        enable_proxy: bool = False,
    ) -> AsyncContextManager[AsyncSession]:
        """
        Async open a Browserbase session and provide access to actions on that
        session. The session will close automatically once the block is exited.

        >>> async with bbase.session() as session:
                print(session.id)
        """
        # A derived class will create the session from the given options,
        # then use the _asession_manager to create the async context manager.

    #
    # Session management utilities for use in a session object
    #

    def get_http_headers(
        self, session: Optional[BaseSession] = None
    ) -> Headers:
        """
        Get the headers necessary for HTTP communication to the API.

        This will include the required API key.
        """
        headers = Headers({"x-bb-api-key": self._api_key})
        if session is not None and session.id:
            headers["session-id"] = session.id

        return headers

    def get_cdp_url(
        self, session: Optional[BaseSession] = None, **kwargs
    ) -> str:
        """
        Get the Chrome Dev Protocol URL

        If a session is provided, gets the URL for the given session.
        Any additional arguments are treated as url parameters.
        """
        kwargs["apiKey"] = self._api_key
        if session:
            kwargs["sessionId"] = session.id

        return f"{SESSION_CDP_URL}?{urlencode(kwargs)}"

    #
    # Session management commands
    #

    def list_sessions(
        self, status: Optional[SESSIONSTATUS] = None
    ) -> list[SyncSession]:
        """
        Return a list of all sessions.

        status can be one of RUNNING, ERROR, TIMED_OUT or COMPLETED
        to limit the query to sessions of that status.
        """
        headers = self.get_http_headers()
        if status is not None:
            params = {"status": status}
        else:
            params = {}

        response = httpx.get(SESSIONS_API_URL, params=params, headers=headers)
        response.raise_for_status()

        return [
            SyncSession.from_api_response(self, d) for d in response.json()
        ]

    async def alist_sessions(
        self, status: Optional[SESSIONSTATUS] = None
    ) -> list[AsyncSession]:
        """
        Return a list of all sessions.

        status can be one of RUNNING, ERROR, TIMED_OUT or COMPLETED
        to limit the query to sessions of that status.
        """
        headers = self.get_http_headers()
        if status is not None:
            params = {"status": status}
        else:
            params = {}

        async with httpx.AsyncClient() as client:
            response = await client.get(
                SESSIONS_API_URL, params=params, headers=headers
            )
        response.raise_for_status()

        return [
            AsyncSession.from_api_response(self, d) for d in response.json()
        ]
