"""Error tracking service API and setup."""

import sentry_sdk

from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.pyramid import PyramidIntegration
from pyramid.settings import asbool

from h_pyramid_sentry.event_filter import get_before_send


def report_exception(exc=None):
    """
    Report an exception to the error tracking service.

    If the given ``exc`` is :obj:`None` then the most recently raised exception
    will be reported.

    :arg exc: the exception to report
    :type exc: :class:`Exception`, :obj:`None`, or a :func:`sys.exc_info` tuple
    """
    sentry_sdk.capture_exception(exc)


DEFAULTS_OPTIONS = {
    "send_default_pii": True,
    "integrations": [CeleryIntegration(), PyramidIntegration()],
}


def includeme(config):
    """Set up the error tracking service."""
    filters = [
        # Allow functions to be passed as strings: e.g. "module.function"
        config.maybe_dotted(_filter)
        for _filter in config.registry.settings.get("h_pyramid_sentry.filters", [])
    ]

    if asbool(config.registry.settings.get("h_pyramid_sentry.retry_support")):
        from h_pyramid_sentry.filters.pyramid import is_retryable_error

        filters.append(is_retryable_error)
        config.scan("h_pyramid_sentry.subscribers")

    init_options = {
        **DEFAULTS_OPTIONS,
        **config.registry.settings.get("h_pyramid_sentry.init", {}),
    }

    sentry_sdk.init(before_send=get_before_send(filters), **init_options)
