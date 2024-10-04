"""
Implementation of the BaseSession that performs asyncronous API interactions.
"""

from logging import getLogger

import httpx

from .api_models import (
    DebugConnectionURLs,
    SessionLog,
    SessionRecording,
    SessionResponse,
)
from .base_session import SESSIONS_API_URL, BaseSession

logger = getLogger("browserbase")
logger.propagate = False  # Don't roll logs up to the root logger


class AsyncSession(BaseSession):
    """
    Object for interacting with a Browserbase session asyncronously.

    None of the session classes are meant to be used directly,
    but are passed as return values to various actions on the
    core Browserbase class.
    """

    #
    # Session management
    #

    async def start(self) -> str:
        """
        Explicitly start the session, if not already started.

        Returns the session ID.
        """
        if self._api_response is not None:
            logger.info("session already started")
            return self.id

        headers = self._browserbase.get_http_headers()
        json = self._session_options.model_dump()

        async with httpx.AsyncClient() as client:
            response = await client.post(
                SESSIONS_API_URL, json=json, headers=headers
            )
            response.raise_for_status()

        self._api_response = SessionResponse.model_validate_json(response.text)

        return self.id

    async def end(self):
        """
        End the session if it's running.
        """
        if self._api_response is None:
            logger.info("session.end called, but the session is not started.")
            return

        url = f"{SESSIONS_API_URL}/{self.id}"
        headers = self._browserbase.get_http_headers()
        json = self._end_session_options.model_dump()

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=json, headers=headers)
            response.raise_for_status()

        self._api_response = SessionResponse.model_validate_json(response.text)

    #
    # Other session interactions
    #

    async def get_zipped_downloads(self, file_io) -> None:
        """
        Get a zipped archive of the files that were downloaded during the session.

        The ZIP file is downloaded then written to the provided file handle.

        file_io: An open async i/o handle that has an awaitable write method.

        To retrieve the file and write it to "download.zip", use the following:

        >>> async with bbase.session() as session:
        >>>     # Do some action to download a file to the remote browser
        >>>     pass

        >>> async with aiopen("download.zip") as file:
        >>>     await session.get_zipped_downloads(file)

        """
        url = f"{SESSIONS_API_URL}/{self.id}/downloads"
        headers = self._browserbase.get_http_headers()
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
        # Raise an exception if there wasn't a good response
        response.raise_for_status()

        # Write the zipfile data to the given IO
        await file_io.write(response.content)

    async def get_live_urls(self) -> DebugConnectionURLs:
        """
        Get URLs that can be used to connect to a live session.
        """
        url = f"{SESSIONS_API_URL}/{self.id}/debug"
        headers = self._browserbase.get_http_headers()
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)

        # Raise an exception if there wasn't a good response from the endpoint
        response.raise_for_status()

        return DebugConnectionURLs.model_validate_json(response.text)

    async def get_logs(self) -> list[SessionLog]:
        """
        Get all the logs for the session.
        """
        url = f"{SESSIONS_API_URL}/{self.id}/logs"
        headers = self._browserbase.get_http_headers()
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)

        # Raise an exception if there wasn't a good response from the endpoint
        response.raise_for_status()

        # Use the HTTPX JSON parser for initial decoding
        data = response.json()

        # Convert all data into valid SessionLog objects
        return [SessionLog.model_validate(d) for d in data]

    async def get_recording(self) -> list[SessionRecording]:
        """
        Get all the recordings for the session.
        """
        url = f"{SESSIONS_API_URL}/{self.id}/recording"
        headers = self._browserbase.get_http_headers()
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
        # Raise an exception if there wasn't a good response from the endpoint
        response.raise_for_status()

        # Use the HTTPX JSON parser for initial decoding
        data = response.json()

        # Convert all data into valid SessionLog objects
        return [SessionRecording.model_validate(d) for d in data]
