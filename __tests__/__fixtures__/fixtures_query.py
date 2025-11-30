import pytest
import logging
import asyncio
from django.http import (HttpResponse, HttpRequest)
from django.contrib.sessions.middleware import SessionMiddleware
from logs import configure_logging

configure_logging(logging.DEBUG)
log = logging.getLogger(__name__)


#
@pytest.fixture
def fix_user_registration():
    @pytest.mark.django_db
    async def fix_persone_valid(
        fix_get_session, factory,
        email, password,password_confirm,  role
    ):
        from django.contrib.auth.models import AnonymousUser
        text_test = "[%s]:" % fix_persone_valid.__name__,
        log.info(f"%s START TEST a REGISTRATION - WHERE IS: 'email': %s" % (text_test, email) )

        try:
            request = factory.post("/person/", content_type="application/json")
            request.__setattr__("user", AnonymousUser())
            request.__setattr__(
                "data",
                {
                    "email": email,
                    "password": password,
                    "password_confirm": password_confirm,
                    "category": role,
                },
            )
            # CREATE AND ADDING a SESSION FOR USER's ACTIVATION
            request = await fix_get_session(request)
            return request
        except Exception as e:
            log.error("%s: %s", (text_test, e.args[0]))
            return False
    return fix_persone_valid

@pytest.fixture
def fix_get_session():
    async def factory(request: HttpRequest) -> HttpRequest:
        # CREATE AND ADDING a SESSION
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request_is_saving = request.session.save
        await asyncio.to_thread(request_is_saving)
        return request

    return factory
