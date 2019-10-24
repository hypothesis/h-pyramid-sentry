Hypothesis Pyramid Sentry Extension
===================================

**At the moment the library is mostly being used as an experimental testing
ground and therefore is not recommended for general use.**

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
| `h_pyramid_sentry.retry_support` | Enable retry detection and filtering |

As per the [Sentry docs](https://docs.sentry.io/error-reporting/configuration/?platform=python#dsn), the
environment variable `SENTRY_DSN` will be automatically read if set, although this can
also be passed along with any other Sentry SDK options via `h_pyramid_sentry.init`.

Hacking
-------

### Installing h-pyramid-sentry in a development environment

#### You will need

* [Git](https://git-scm.com/)

* [pyenv](https://github.com/pyenv/pyenv)
  Follow the instructions in the pyenv README to install it.
  The Homebrew method works best on macOS.
  On Ubuntu follow the Basic GitHub Checkout method.

#### Clone the git repo

```terminal
git clone https://github.com/hypothesis/h-pyramid-sentry.git
```

This will download the code into a `h-pyramid-sentry` directory
in your current working directory. You need to be in the
`h-pyramid-sentry` directory for the rest of the installation
process:

```terminal
cd h-pyramid-sentry
```

#### Run the tests

```terminal
make test
```

**That's it!** You’ve finished setting up your h-pyramid-sentry
development environment. Run `make help` to see all the commands that're
available for linting, code formatting, packaging, etc.

### Updating the Cookiecutter scaffolding

This project was created from the
https://github.com/hypothesis/h-cookiecutter-pypackage/ template.
If h-cookiecutter-pypackage itself has changed since this project was created, and
you want to update this project with the latest changes, you can "replay" the
cookiecutter over this project. Run:

```terminal
make template
```

**This will change the files in your working tree**, applying the latest
updates from the h-cookiecutter-pypackage template. Inspect and test the
changes, do any fixups that are needed, and then commit them to git and send a
pull request.

If you want `make template` to skip certain files, never changing them, add
these files to `"options.disable_replay"` in
[`.cookiecutter.json`](.cookiecutter.json) and commit that to git.

If you want `make template` to update a file that's listed in `disable_replay`
simply delete that file and then run `make template`, it'll recreate the file
for you.
