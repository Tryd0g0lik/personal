"""
__tests__/__fixtures__/fixtures_db.py
"""

import asyncio

from typing import Optional, Any, Coroutine

import pytest
import logging
from django.db import models
from django.http import HttpRequest, HttpResponse
from logs import configure_logging

configure_logging(logging.INFO)
log = logging.getLogger(__name__)

type TypeModelDB = Optional[models.Model]


@pytest.fixture
def f_clear_db():
    async def factory(Name_db: TypeModelDB):
        log.info("[f_clear_db]: Clear db (%s) - start" % Name_db.__class__.__name__)
        try:
            filter_list = [view.delete async for view in Name_db.objects.all()]
            coroutine_list = []
            for item in filter_list:
                coroutine_list.append(asyncio.to_thread(lambda: item()))
            await asyncio.gather(*coroutine_list)
            return True
        except Exception as e:
            log.error(
                "[f_clear_db]: DB '%s' ERROR => %s",
                (
                    Name_db.__class__.__name__,
                    e.args[0],
                ),
            )
            return False

    return factory
