
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
