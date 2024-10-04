"""
Selenium session object implements Selenium specific session logic.
"""

from typing import Optional

from selenium.webdriver.remote.webdriver import WebDriver

from ..sync_session import SyncSession


class SeleniumSession(SyncSession):
    _driver: Optional[WebDriver] = None

    @property
    def driver(self) -> WebDriver:
        if self._driver is None:
            raise RuntimeError("session.driver has not been set.")
        return self._driver

    @driver.setter
    def driver(self, new_driver: WebDriver) -> None:
        if self._driver is not None:
            raise RuntimeError("Attempt to reassign session.driver")
        self._driver = new_driver
