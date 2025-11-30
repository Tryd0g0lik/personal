"""
__tests__/tests_person/test_user_registrition.py
"""
import pytest
import logging
from rest_framework.test import APIRequestFactory
from django.contrib.auth.models import AnonymousUser
from __tests__.__fixtures__.fixtures_db import f_clear_db
from __tests__.__fixtures__.fixtures_query import fix_user_registration, fix_get_session
from logs import configure_logging
from person.models import User
from person.models_person.model_role import RoleModel
from person.views import CSRFTokenView

log = logging.getLogger(__name__)
configure_logging(logging.INFO)



@pytest.mark.parametrize(
    "email, password, password_confirm, role, expected",
    [
        ("work1@mail.ru", "gKU12pgP5hB", "gKU12pgP5hB", "staff", True),
        (" work2@mail.ru ", " gKU12pgP5hB ", "gKU12pgP5hB", "staff", True),
        ("work3@mail.ru", "gKU12pgP5hB", " gKU12pgP5hB ", "staff", True),
        ("work4@mail.ru", "gKU12pgP5hB", "gKU12pgP5hB", " staff ", True),
    ],
)
@pytest.mark.person_creat_valid
@pytest.mark.django_db
async def test_person_valid(f_clear_db, fix_user_registration,fix_get_session,
                            email, password, password_confirm, role, expected) -> None:
    from person.views_api.views_person_api import UserViews
    text_test = "[%s]:" % test_person_valid.__name__,
    await f_clear_db(User)
    await f_clear_db(RoleModel)
    log.info(
        "%s START TEST WHERE - 'email': %s & 'password': %s & 'password_confirm': %s & 'role': %s & 'expected': %s"
        % (
            text_test,
            email,
            password,
            password_confirm,
            role,
            expected,
        )
    )
    fuctory = APIRequestFactory()
    await fix_user_registration(fix_get_session, fuctory, email, password, password_confirm, role)
    request = fuctory.post("/person/", content_type="application/json")
    request.__setattr__("user", AnonymousUser())
    request.user.__setattr__("is_active", False)
    request.__setattr__(
        "data",
        {
            "email": email,
            "password": password,
            "password_confirm": password_confirm,
            "role": role,
        },
    )
    log.info("%s GET REQUEST.data['email'] %s" % (text_test, email))
    response = await UserViews().create(request)

    res_bool = True if response.status_code < 300 else False
    assert res_bool == expected
    assert isinstance(response.data, dict)
    log.info("%s GET REQUEST.data %s" % (text_test, response.data.__str__()))
    # assert not isinstance(response.data[0].values()[0], str)
    assert not response.data.get("error")

    log.info(
        "%s Test completed. RESPONSE 'response.data': %s" % (text_test, response.data)
    )
