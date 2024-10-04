"""
Pydantic models for communication with the Browserbase API.
"""

from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

BROWSERTYPE = Literal["chrome", "firefox", "edge", "safari"]
DEVICETYPE = Literal["desktop", "mobile"]
OPERATINGSYSTEM = Literal["windows", "macos", "linux", "ios", "android"]
SESSIONSTATUS = Literal[
    "NEW",
    "CREATED",
    "ERROR",
    "RUNNING",
    "REQUEST_RELEASE",
    "RELEASING",
    "COMPLETED",
    "TIMED_OUT",
]


class BaseSchema(BaseModel):
    """
    Base class for all API schema derived models.
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    def model_dump_json(
        self, by_alias=True, exclude_null=True, exclude_unset=True, **kwargs
    ) -> str:
        """
        Dump to JSON, using most common parameters for the Browserbase API.
        """
        return super().model_dump_json(
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_none=exclude_null,
            **kwargs,
        )

    def model_dump(
        self, by_alias=True, exclude_null=True, exclude_unset=True, **kwargs
    ) -> dict[str, Any]:
        """
        Dump to dictionary, using most common parameters for the Browserbase API.
        """
        return super().model_dump(
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_none=exclude_null,
            **kwargs,
        )


class Screen(BaseSchema):
    """
    Dimensions of the browser screen.
    """

    max_height: Optional[int]
    max_width: Optional[int]
    min_height: Optional[int]
    min_width: Optional[int]


class Fingerprint(BaseSchema):
    """
    Options for changing how the browser is represented.
    """

    browser_list_query: Optional[str] = None
    http_version: Optional[int] = None
    browsers: Optional[list[BROWSERTYPE]] = None
    devices: Optional[list[DEVICETYPE]] = None
    locales: Optional[list[str]] = None
    operating_systems: Optional[list[OPERATINGSYSTEM]] = None
    screen: Optional[Screen] = None


class Viewport(BaseSchema):
    width: Optional[int] = None
    height: Optional[int] = None


class BrowserSettings(BaseSchema):
    fingerprint: Optional[Fingerprint] = None
    viewport: Optional[Viewport] = None


class CreateSessionOptions(BaseSchema):
    def __init__(
        self,
        viewport: Optional[Viewport] = None,
        fingerprint: Optional[Fingerprint] = None,
        browser_settings: Optional[BrowserSettings] = None,
        **kwargs,
    ):

        # Pull out the viewport and fingerprint, if defined,
        # then wrap them in a BrowserSettings object as needed.
        if any((viewport, fingerprint)):
            browser_settings = (
                browser_settings.copy()
                if browser_settings
                else BrowserSettings()
            )
            # Only set these if defined
            if viewport is not None:
                browser_settings.viewport = viewport
            if fingerprint is not None:
                browser_settings.fingerprint = fingerprint

            kwargs["browser_settings"] = browser_settings

        elif browser_settings:
            # If the browser_settings were defined, ensure they're used.
            kwargs["browser_settings"] = browser_settings

        super().__init__(**kwargs)

    project_id: Optional[str] = None
    extension_id: Optional[str] = None
    browser_settings: Optional[BrowserSettings] = None
    timeout: Optional[int] = None
    keep_alive: Optional[bool] = None
    status: Optional[SESSIONSTATUS] = None


class SessionResponse(BaseSchema):
    id: str
    project_id: str
    created_at: datetime
    started_at: datetime
    updated_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    status: Optional[SESSIONSTATUS] = None
    task_id: Optional[str] = None
    proxy_bytes: Optional[int] = None
    expires_at: Optional[datetime] = None
    avg_cpu_usage: Optional[float] = None
    memory_usage: Optional[int] = None
    details: Optional[str] = None
    logs: Optional[str] = None


class SessionRecording(BaseSchema):
    type: Optional[str] = None
    time: Optional[str] = None
    data: Optional[dict] = None


class DebugConnectionURLs(BaseSchema):
    debugger_fullscreen_url: Optional[str] = None
    debugger_url: Optional[str] = None
    ws_url: Optional[str] = None


class SessionLogRequest(BaseSchema):
    timestamp: Optional[str]
    params: Optional[dict]
    raw_body: Optional[str] = None


class SessionLogResponse(BaseSchema):
    timestamp: Optional[datetime]
    result: Optional[dict]
    raw_body: Optional[str] = None


class SessionLog(BaseSchema):
    session_id: Optional[str] = None
    id: str
    timestamp: Optional[datetime] = None
    method: Optional[str] = None
    request: Optional[SessionLogRequest] = None
    response: Optional[SessionLogResponse] = None
    page_id: Optional[str] = None
