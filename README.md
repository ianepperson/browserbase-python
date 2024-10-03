# Browserbase Python Package
[Browserbase](https://browserbase.com/) is a serverless platform for running headless browsers, it offers advanced debugging, session recordings, stealth mode, integrated proxies and captcha solving.

## Installation and setup

- Get an API key from [browserbase.com](https://browserbase.com) and set it in the environment `BROWSERBASE_API_KEY` environment variable.
- Get the Project ID from the [Browserbase settings](https://www.browserbase.com/settings) page, and set it in
  the `BRWOSERBASE_PROJECT_ID` environment variable.
- Install the required dependencies:

```sh
pip install browserbase
```
or, if you're using [Poetry](https://python-poetry.org) to manage your Python environments:

```sh
poetry install browserbase
```

### Automation Framework

The core Browserbase library provides an interface to the Browserbase services, but most users will want to also use
an automation framework like [Playwright](https://playwright.dev/python/) (recommended) or [Selenium](https://selenium-python.readthedocs.io).
This package provides helper methods to streamline those interactions.

To install the extra requirements, tell your package installer to include
- `playwright`
- `selenium`
- or both `selenium,playwright`

Like so:

```sh
pip install browserbase[playwright]
```
with Poetry:

```sh
poetry add --extras "playwright"
```

## Usage

```python
from browserbase import Browserbase

# Initialize the library
bbase = Browserbase()

# Create a simple session
with bbase.session() as session:
    print(session.url)

# Get a list of all sessions
bbase.list_sessions()
```

#### Async

The available Async methods start with `a`:

```python
# Create a simple async session
awync with bbase.asession() as session:
    print(session.url)

# Get a list of all sessions
await bbase.alist_sessions()
```
## Usage with Playwright

When creating a session, a [Playwright Page](https://playwright.dev/python/docs/api/class-page)
is available via the session `page` property to control the remote Browserbase browser.

```python
from browserbase.playwright import Browserbase

# Initialize the library
bbase = Browserbase()

# Create a session
with bbase.session() as session:
    # The session.page object is a Playwright Page
    session.page.goto("https://www.sfmoma.com")
    print(session.page.title)
```

If you don't need access to the Browserbase session object nor need to provide any extra session options,
you can ask for just a Playwright page. Doing so saves an extra API call behind the scenes,
and so is a bit faster.

```python
with bbase.page() as page:
    page.goto("https://www.sfmoma.com")
    print(page.title)
```

#### Async

The Playwright async Page object is returned when using the async methods.

```python
# Create an async session
async with bbase.asession() as session:
    # The session.page object is a Playwright Page
    await session.page.goto("https://www.sfmoma.com")
    print(session.page.title)
```

```python
async with bbase.apage() as page:
    await page.goto("https://www.sfmoma.com")
    print(page.title)
```

## Usage with Selenium

When creating a session, a [Selenium WebDriver](https://selenium-python.readthedocs.io/api.html#selenium.webdriver.remote.webdriver.WebDriver)
is available via the session `driver` property to control the remote Browserbase browser.

```python
from browserbase.selenium import Browserbase

# Initialize the library
bbase = Browserbase()

# Create a session
with bbase.session() as session:
    # The session.driver object is a Selenium WebDriver
    session.driver.get("https://www.sfmoma.com")
    print(session.page.title)
```

#### Async

The Selenium Python library does not support async operations.
