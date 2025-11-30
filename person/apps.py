"""
person/apps.py
"""

import asyncio
import logging
from django.apps import AppConfig
from logs import configure_logging

configure_logging(logging.INFO)
log = logging.getLogger(__name__)


class PersonConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "person"

    def ready(self):
        asyncio.run(self.installer())

    async def installer(self):
        from person.models_person.model_role import RoleModel

        # ==== Here, list of roles will create
        roles = ["staff", "admin", "user", "visitor", "superuser"]
        tasks = []
        try:

            for role in roles:
                tasks.append(
                    asyncio.to_thread(
                        lambda r=role: RoleModel.objects.get_or_create(name=r)
                    )
                )
            print(f"roles_tasks: == {tasks}")
            await asyncio.gather(*tasks)
            return True
        except Exception as e:
            text_e = "[%s.%s]: ERROR => %s" % (
                self.__class__.__name__,
                self.installer.__name__,
                e.args[0],
            )
            log.error(text_e)
            return False
