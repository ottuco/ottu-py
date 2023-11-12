import pytest


@pytest.fixture
def ottu():
    from ottu.contrib.django.core.ottu import _generate_instance

    return _generate_instance()


@pytest.fixture
def custom_wh_error(settings):
    settings.DJ_OTTU_RAISE_WH_ERROR = True
