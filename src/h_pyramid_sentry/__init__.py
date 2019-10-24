"""Error tracking service API and setup."""


import re

import sentry_sdk
from pyramid.settings import asbool
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.logging import ignore_logger
from sentry_sdk.integrations.pyramid import PyramidIntegration

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


DEFAULT_OPTIONS = {
    "send_default_pii": True,
    "integrations": [CeleryIntegration(), PyramidIntegration()],
}
OPTION_PATTERN = re.compile(r"^h_pyramid_sentry\.init\.(.*)$")


def includeme(config):
    """Set up the error tracking service."""
    filters = [
        # Allow functions to be passed as strings: e.g. "module.function"
        config.maybe_dotted(_filter)
        for _filter in config.registry.settings.get("h_pyramid_sentry.filters", [])
    ]

    if asbool(config.registry.settings.get("h_pyramid_sentry.retry_support")):
        # pylint:disable=import-outside-toplevel
        # This is here to lazy load only when required
        from h_pyramid_sentry.filters.pyramid import is_retryable_error

        filters.append(is_retryable_error)
        config.scan("h_pyramid_sentry.subscribers")

    init_options = {**DEFAULT_OPTIONS}
    for key, value in config.registry.settings.items():
        match = OPTION_PATTERN.match(key)
        if match:
            init_options[match.group(1)] = value

    # exc_logger (which comes from
    # https://docs.pylonsproject.org/projects/pyramid_exclog/) logs all
    # exceptions with log level ERROR, and then all of these get picked up by
    # sentry_sdk's enabled-by-default logging integration
    # (https://docs.sentry.io/platforms/python/logging/).
    #
    # This means that:
    #
    # 1. All exceptions get reported via exc_logger instead of via sentry_sdk's
    # normal route (of intercepting raised exceptions)
    #
    # 2. Some handled exceptions that wouldn't have been reported via the
    # normal route now do get reported because exc_logger logs them as errors.
    #
    # We don't want either of these two things to happen so tell sentry_sdk's
    # logging integration to ignore exc_logger (see
    # https://docs.sentry.io/platforms/python/logging/#ignoring-a-logger).
    #
    # If pyramd_exclog isn't installed this will just have no effect.
    ignore_logger("exc_logger")

    sentry_sdk.init(before_send=get_before_send(filters), **init_options)
