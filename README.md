<a href="https://github.com/hypothesis/h-pyramid-sentry/actions/workflows/ci.yml?query=branch%3Amain"><img src="https://img.shields.io/github/actions/workflow/status/hypothesis/h-pyramid-sentry/ci.yml?branch=main"></a>
<a href="https://pypi.org/project/h-pyramid-sentry"><img src="https://img.shields.io/pypi/v/h-pyramid-sentry"></a>
<a><img src="https://img.shields.io/badge/python-3.9 | 3.8-success"></a>
<a href="https://github.com/hypothesis/h-pyramid-sentry/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-BSD--2--Clause-success"></a>
<a href="https://github.com/hypothesis/cookiecutters/tree/main/pypackage"><img src="https://img.shields.io/badge/cookiecutter-pypackage-success"></a>
<a href="https://black.readthedocs.io/en/stable/"><img src="https://img.shields.io/badge/code%20style-black-000000"></a>

# Hypothesis Pyramid Sentry Extension

A library which integrates Sentry logging into Pyramid with the ability to filter out unwanted messages.

This is a Pyramid extension that wraps
[sentry-sdk's Pyramid integration](https://docs.sentry.io/platforms/python/pyramid/)
and adds some additional customization and features.

Features
--------

* Initializes sentry-sdk with its Pyramid integration for you.
  Your app just has to set any `"h_pyramid_sentry.*"` settings that you want
  and then do `config.include("h_pyramid_sentry")` (see instructions below for details).

* Prevents retryable exceptions from being reported to Sentry if your app is using
  [pyramid_retry](http://docs.pylonsproject.org/projects/pyramid-retry/en/latest/)
  and the request is going to be retried
  (requires the `"h_pyramid_sentry.retry_support": True` setting, see below).

  Retryable exceptions will still be reported to Sentry if the request is not
  going to be retried again because it has run out of retry attempts or because
  one of the retries fails with a non-retryable exception. When this happens
  only the exception from the request's final attempt is reported to Sentry, so
  you get a single Sentry event per request not multiple, but information about
  the previous failed attempts' exceptions is added to the single Sentry event.

* Ignores errors logged by `exc_logger` if your app is using
  [pyramid_exclog](https://docs.pylonsproject.org/projects/pyramid_exclog/en/latest/).

  pyramid_exclog logs all exceptions with log-level ERROR, and these all
  get picked up by sentry_sdk's [enabled-by-default logging integration](https://docs.sentry.io/platforms/python/logging/).
  This would mean that all exceptions in Sentry appear to come from
  exc_logger, and that some handled exceptions that wouldn't normally be
  reported to Sentry now _would_ get reported. This extension prevents the
  interference by telling sentry_sdk to ignore exc_logger.

* Provides a convenient method for apps to register their own filters for
  exceptions and logged errors that they don't want to be reported to Sentry.
  See the `"h_pyramid_sentry.filters"` setting below.

Usage
-----

```python
config.add_settings({...})  # See below for available settings.
config.include("h_pyramid_sentry")
```

Filters
-------

In your Pyramid configuration you can provide a list of filter functions in the
setting `h_pyramid_sentry.filters`.

These functions are passed [Event](h_pyramid_sentry/event.py) objects which
they can inspect. If the function returns `True`, then the event is not sent to
Sentry.

For example to prevent reporting of `ValueError`s:

```python
config.add_settings({
    "h_pyramid_sentry.filters": [
        lambda event: instanceof(event.exception, ValueError)
    ],
})
```

Settings
--------

The extension will listen to the following Pyramid deployment settings:

| Pyramid setting        | Effect |
|------------------------|---------------|
| `h_pyramid_sentry.init` | A dict of any [options understood by `sentry_sdk.init()`](https://docs.sentry.io/error-reporting/configuration/?platform=javascript#common-options) |
| `h_pyramid_sentry.filters` | A list of functions to apply as filters |
| `h_pyramid_sentry.retry_support` *| Enable retry detection and filtering|
| `h_pyramid_sentry.celery_support` *| Enable [Celery support for Sentry](https://docs.sentry.io/platforms/python/celery/) |
| `h_pyramid_sentry.sqlalchemy_support` *| Enable [SQLAlchemy support for Sentry](https://docs.sentry.io/platforms/python/sqlalchemy/) |

_* Enabling retry or celery support requires your application to list the relevant dependency (`pyramid_retry` or `celery`) as a dependency._ 

As per the [Sentry docs](https://docs.sentry.io/error-reporting/configuration/?platform=python#dsn), the
environment variable `SENTRY_DSN` will be automatically read if set, although this can
also be passed along with any other Sentry SDK options via `h_pyramid_sentry.init`.

## Setting up Your Hypothesis Pyramid Sentry Extension Development Environment

First you'll need to install:

* [Git](https://git-scm.com/).
  On Ubuntu: `sudo apt install git`, on macOS: `brew install git`.
* [GNU Make](https://www.gnu.org/software/make/).
  This is probably already installed, run `make --version` to check.
* [pyenv](https://github.com/pyenv/pyenv).
  Follow the instructions in pyenv's README to install it.
  The **Homebrew** method works best on macOS.
  The **Basic GitHub Checkout** method works best on Ubuntu.
  You _don't_ need to set up pyenv's shell integration ("shims"), you can
  [use pyenv without shims](https://github.com/pyenv/pyenv#using-pyenv-without-shims).

Then to set up your development environment:

```terminal
git clone https://github.com/hypothesis/h-pyramid-sentry.git
cd h-pyramid-sentry
make help
```

## Releasing a New Version of the Project

1. First, to get PyPI publishing working you need to go to:
   <https://github.com/organizations/hypothesis/settings/secrets/actions/PYPI_TOKEN>
   and add h-pyramid-sentry to the `PYPI_TOKEN` secret's selected
   repositories.

2. Now that the h-pyramid-sentry project has access to the `PYPI_TOKEN` secret
   you can release a new version by just [creating a new GitHub release](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository).
   Publishing a new GitHub release will automatically trigger
   [a GitHub Actions workflow](.github/workflows/pypi.yml)
   that will build the new version of your Python package and upload it to
   <https://pypi.org/project/h-pyramid-sentry>.

## Changing the Project's Python Versions

To change what versions of Python the project uses:

1. Change the Python versions in the
   [cookiecutter.json](.cookiecutter/cookiecutter.json) file. For example:

   ```json
   "python_versions": "3.10.4, 3.9.12",
   ```

2. Re-run the cookiecutter template:

   ```terminal
   make template
   ```

3. Commit everything to git and send a pull request

## Changing the Project's Python Dependencies

To change the production dependencies in the `setup.cfg` file:

1. Change the dependencies in the [`.cookiecutter/includes/setuptools/install_requires`](.cookiecutter/includes/setuptools/install_requires) file.
   If this file doesn't exist yet create it and add some dependencies to it.
   For example:

   ```
   pyramid
   sqlalchemy
   celery
   ```

2. Re-run the cookiecutter template:

   ```terminal
   make template
   ```

3. Commit everything to git and send a pull request

To change the project's formatting, linting and test dependencies:

1. Change the dependencies in the [`.cookiecutter/includes/tox/deps`](.cookiecutter/includes/tox/deps) file.
   If this file doesn't exist yet create it and add some dependencies to it.
   Use tox's [factor-conditional settings](https://tox.wiki/en/latest/config.html#factors-and-factor-conditional-settings)
   to limit which environment(s) each dependency is used in.
   For example:

   ```
   lint: flake8,
   format: autopep8,
   lint,tests: pytest-faker,
   ```

2. Re-run the cookiecutter template:

   ```terminal
   make template
   ```

3. Commit everything to git and send a pull request
