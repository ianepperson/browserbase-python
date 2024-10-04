"""
A class to use with Selenium to connect to a Browserbase service.

For internal use.
"""

from typing import Optional
from selenium.webdriver import Remote, ChromeOptions
from selenium.webdriver.remote.remote_connection import RemoteConnection
from selenium.webdriver.remote.webdriver import WebDriver

from browserbase.selenium.sl_session import SeleniumSession
from .sl_session import SeleniumSession


class BrowserbaseConnection(RemoteConnection):
    """
    Manage a single session with Browserbase.
    """

    _session_id: SeleniumSession

    def __init__(self, session: SeleniumSession, *args, **kwargs):
        self._session = session
        super().__init__(*args, **kwargs)

    def get_remote_connection_headers(self, parsed_url, keep_alive=False):
        """
        Override to add the required Browserbase values.
        """
        headers = super().get_remote_connection_headers(parsed_url, keep_alive)

        # Update headers to include the Browserbase required information
        bb_headers = self._session._browserbase.get_http_headers(self._session)
        headers.update(bb_headers)

        return headers

    def get_driver(self, options: Optional[ChromeOptions] = None) -> WebDriver:
        """
        Return a driver for this connection.

        options are a selenium.webdriver.ChromeOptions object.
        """
        if options is None:
            options = ChromeOptions()

        return Remote(self, options=options)
