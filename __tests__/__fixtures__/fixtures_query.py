import pytest
import logging
from django.http import (HttpResponse, HttpRequest)
from logs import configure_logging

configure_logging(logging.DEBUG)
log = logging.getLogger(__name__)

@pytest.fixture
def f_get_session():
