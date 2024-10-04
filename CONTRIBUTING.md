# Contributing

This document provides an overview on how to get started contributing to this package.

Check the Layout section on how to find different objects and logic.

## Setup

## Install System Dependencies

Bootstrapping is still an issue with Python. Once you have the following three tools installed, things get easier.

If you already have Poetry and Poe-the-Poet installed, skip ahead.

#### PipX

The [pipx](https://pipx.pypa.io/stable/) tool is used to install other Python based tools easily.

Yes, this might require installing [Homebrew](https://brew.sh) (for Macs) or [Scoop](https://scoop.sh) (for Windows). Yes this kinda sucks,
but it's worth the pain.

#### Poetry

[Poetry](https://python-poetry.org) is a tool that makes managing Python virtual environments, dependencies and packages easy.
It can be [installed](https://python-poetry.org/docs/) with pipx.

```bash
pipx install poetry
```

#### Poe the Poet

[Poe the Poet](https://poethepoet.natn.io/) is a task runner that works well with Poetry.
It can also be [installed](https://poethepoet.natn.io/installation.html) with pipx.

```bash
pipx install poethepoet
```

### Install the Python Environment

Navigate a console to this folder, then run:

```bash
poetry install
```

Poetry should install everything necessary.

### Use the Poetry Shell

To start a shell with the proper virtual environment selected and libraries loaded,

```bash
> poetry shell
(xyz) >
```

### Run the Tests

From the Poetry shell, run:

```bash
> pytest
```

To include the coverage information, use:
```bash
> pytest --cov=browserbase --cov-report term-missing
```

Coverage should always be over 90%. At the time of this writing, it's 93%

### Classes Overview

In general, each class resides in its own file. The `__init__.py` file in any given folder will import
the items that are to be used by the consumers of this package.

#### Browserbase

* `core.BrowserbaseCore`: The abstract class that all Browserbase classes inherit from.
  * `browserbase.Browserbase`: The most simple implementation of the above.
  * `playwright.pl_browserbase.Browserbase`: Implementation that also manages Playwright sessions.
  * `selenium.sl_browserbase.Browserbase`: Implementation that also manages Selenium sessions.

#### Session

* `base_session.BaseSession`: Base class for all sessions. Implments no API interactions.
  * `sync_session.SyncSession`: Implements all session-specific API interactions.
    * `playwright.pl_session.PlaywrightSyncSession`: Adds in Playwright specific logic
    * `selenium.sl_session.SeleniumSession`: Adds in Selenium specific logic
  * `async_session.AxyncSession`: Implements all session-specific async API interactions.
    * `playwright.pl_session.PlaywrightAsyncSession`: Adds in Playwright specific logic

## Logs

Uses the [Python standard library logging module](https://docs.python.org/3/library/logging.html).
It does *not* configure any logging output - no Handler, Filter or Formatter settings by default.

Every developer interaction should provide either _one_ `info` log event or raise an exception
in the event of an error. Multiple `debug` or `warning` events may be emitted.

