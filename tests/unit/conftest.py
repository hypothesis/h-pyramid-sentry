"""
The `conftest` module is automatically loaded by pytest and serves as a place
to put fixture functions that are useful application-wide.
"""
import pytest


@pytest.fixture
def Event(patch):
    return patch("h_pyramid_sentry.event_filter.Event")
