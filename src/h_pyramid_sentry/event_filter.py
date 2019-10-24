"""An object which filters events"""
import logging

from h_pyramid_sentry.event import Event
from h_pyramid_sentry.exceptions import FilterNotCallableError

LOG = logging.getLogger(__name__)
LOG_MESSAGE_PREFIX = "Filtering out Sentry event"
LOG_MESSAGE_TEMPLATE = f"{LOG_MESSAGE_PREFIX}: %s"


def get_before_send(filters=None):
    """
    Returns a function which will decide whether the given Sentry event
    should be reported or not.

    Each time an event (for example an uncaught exception or a logged
    error) that would be reported to Sentry happens, ``sentry_sdk`` calls
    this function passing the event first.

    If this function returns ``event_dict`` then the event will be reported
    to Sentry. If this function returns ``None`` the event won't be
    reported.

    See https://docs.sentry.io/error-reporting/configuration/filtering/
    """

    filters = filters or []

    for filter_function in filters:
        if not callable(filter_function):
            raise FilterNotCallableError(filter_function)

    def _before_send(event_dict, hint_dict):
        event = Event(event_dict, hint_dict)

        if any(filter_function(event) for filter_function in filters):
            LOG.info(LOG_MESSAGE_TEMPLATE, hint_dict)
            return None

        return event_dict

    return _before_send
