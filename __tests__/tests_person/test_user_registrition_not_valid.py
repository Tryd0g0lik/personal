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
        ("work1mail.ru", "gKU12pgP5hB", "gKU12pgP5hB", "staff", False),
        (" work2@mailru", " gKU12pgP5hB ", "gKU12pgP5hB", "staff", False),
        ("@mail.ru", "gKU12pgP5hB", " gKU12pgP5hB ", "staff", False),
        ("%work4@mail.ru", "gKU12pgP5hB", "gKU12pgP5hB", " staff ", False),
        ("work5@mail.ru", "gKU12pgP5hBt", "gKU12pgP5hB", " staff ", False),
        ("work6@mail.ru", "", "", " staff ", False),
        ("work7@mail.ru", "  ", "  ", " staff ", False),
        ("work8@mail.ru", "_____", "_____", " staff ", False),
        ("work9@mail.ru", "gKU12pgP5hB", "gKU12pgP5hB", "  ", False),
        ("work10@mail.ru", "gKU12pgP 5hB", "gKU12pgP 5hB", " staff ", False),
        ("work11@mail.ru", "gKU12pgP5hB", "gKU12pgP5hB", "", False),


    ],
)
@pytest.mark.invalid
@pytest.mark.django_db
async def test_person_invalid(f_clear_db, fix_get_session,
                            email, password, password_confirm, role, expected) -> None:
    from person.views_api.views_person_api import UserViews
    text_test = "[%s]:" % test_person_invalid.__name__,
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

    # AnonymousUser
    request = fuctory.post("/api/v1/person/", content_type="application/json")
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

    res_bool = False if response.status_code >= 400 else True
    log.info("%s GET 'res_bool': %s" % (text_test, res_bool))
    assert res_bool == expected
    assert isinstance(response.data, dict)
    log.info("%s GET REQUEST.data %s" % (text_test, response.data.__str__()))
    # assert not isinstance(response.data[0].values()[0], str)
    assert response.data.get("data")
    assert isinstance(response.data.get("data"), str)

    log.info(
        "%s Test completed. RESPONSE 'response.data': %s" % (text_test, response.data)
    )
