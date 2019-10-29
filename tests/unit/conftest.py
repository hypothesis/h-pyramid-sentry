import pytest


@pytest.fixture
def Event(patch):
    return patch("h_pyramid_sentry.event_filter.Event")
