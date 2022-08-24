import logging
from unittest.mock import sentinel

import pytest
from h_matchers import Any

from h_pyramid_sentry.event_filter import LOG_MESSAGE_PREFIX, get_before_send
from h_pyramid_sentry.exceptions import FilterNotCallableError


class TestEventFilter:
    @staticmethod
    def always_filter(*_):
        return True

    @staticmethod
    def never_filter(*_):
        return False

    def test_it_creates_Event(self, Event):
        get_before_send()(sentinel.event_dict, sentinel.hint_dict)

        Event.assert_called_once_with(sentinel.event_dict, sentinel.hint_dict)

    def test_it_filters_when_filter_function_returns_True(self):
        event_filter = get_before_send(
            [
                # Have one that works to ensure we check more
                self.never_filter,
                self.always_filter,
            ]
        )

        assert event_filter(sentinel.event_dict, sentinel.hint_dict) is None

    def test_we_do_not_accept_non_callable_objects_as_filters(self):
        with pytest.raises(FilterNotCallableError):
            get_before_send(["not a function"])

    def test_it_doesnt_filter_if_all_filter_functions_return_False(self):
        event_filter = get_before_send([self.never_filter, self.never_filter])

        assert (
            event_filter(sentinel.event_dict, sentinel.hint_dict) == sentinel.event_dict
        )

    def test_it_logs_when_an_error_is_filtered(self, caplog):
        caplog.set_level(logging.INFO)

        get_before_send([self.always_filter])(sentinel.event_dict, sentinel.hint_dict)

        assert caplog.record_tuples == [
            (Any.string(), logging.INFO, Any.string.containing(LOG_MESSAGE_PREFIX))
        ]
