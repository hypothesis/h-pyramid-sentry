from unittest import mock

import pytest
from h_matchers import Any
from pyramid.testing import testConfig
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.pyramid import PyramidIntegration

from h_pyramid_sentry import includeme, report_exception
from h_pyramid_sentry.filters.pyramid import is_retryable_error


class TestReportException:
    def test_it_reports_the_exception_to_sentry(self, sentry_sdk):
        exc = ValueError("Test exception")

        report_exception(exc)

        sentry_sdk.capture_exception.assert_called_once_with(exc)

    def test_exc_defaults_to_none(self, sentry_sdk):
        report_exception()

        sentry_sdk.capture_exception.assert_called_once_with(None)


class TestIncludeMe:
    def test_it_tells_sentry_sdk_to_ignore_exc_logger(
        self, pyramid_config, ignore_logger
    ):
        includeme(pyramid_config)

        ignore_logger.assert_called_once_with("exc_logger")

    def test_it_initializes_sentry_sdk(self, pyramid_config, sentry_sdk):
        includeme(pyramid_config)

        sentry_sdk.init.assert_called_once_with(
            integrations=[Any.instance_of(PyramidIntegration)],
            send_default_pii=True,
            before_send=Any.function(),
        )

    def test_it_initializes_sentry_sdk_from_config(self, pyramid_config, sentry_sdk):
        pyramid_config.add_settings({"h_pyramid_sentry.init.environment": "test"})

        includeme(pyramid_config)

        sentry_sdk.init.assert_called_once_with(
            integrations=Any(),
            environment="test",
            send_default_pii=Any(),
            before_send=Any.function(),
        )

    def test_it_reads_filter_configuration(self, pyramid_config, get_before_send):
        filter_functions = [lambda *args: 1]  # pragma: no cover
        pyramid_config.registry.settings["h_pyramid_sentry.filters"] = filter_functions

        includeme(pyramid_config)

        get_before_send.assert_called_once_with(filter_functions)

    def test_it_reads_and_enables_retry_detection(
        self, pyramid_config, get_before_send
    ):
        pyramid_config.registry.settings["h_pyramid_sentry.retry_support"] = True
        pyramid_config.scan = mock.create_autospec(
            lambda module: None
        )  # pragma: nocover

        includeme(pyramid_config)

        get_before_send.assert_called_once_with([is_retryable_error])
        pyramid_config.scan.assert_called_with("h_pyramid_sentry.subscribers")

    def test_it_reads_and_enables_celery_support(self, pyramid_config, sentry_sdk):
        pyramid_config.registry.settings["h_pyramid_sentry.celery_support"] = True

        includeme(pyramid_config)

        sentry_sdk.init.assert_called_once_with(
            # This is order sensitive, which we don't honestly care about.
            # As and when list matchers become available we can replace this.
            integrations=[Any(), Any.instance_of(CeleryIntegration)],
            send_default_pii=True,
            before_send=Any.function(),
        )

    @pytest.fixture
    def pyramid_config(self):
        with testConfig() as config:
            yield config


@pytest.fixture(autouse=True)
def get_before_send(patch):
    return patch("h_pyramid_sentry.get_before_send")


@pytest.fixture(autouse=True)
def ignore_logger(patch):
    return patch("h_pyramid_sentry.ignore_logger")


@pytest.fixture(autouse=True)
def sentry_sdk(patch):
    return patch("h_pyramid_sentry.sentry_sdk")
