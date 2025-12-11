"""
person/apps.py
"""
import sys
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
        # Skip during specific management commands
        if self._should_skip():
            return
        # Use Django's built-in system check or signal
        from django.db.models.signals import post_migrate
        from django.dispatch import receiver
        @receiver(post_migrate)
        def create_initial_roles(sender, **kwargs):
            # Only run for this app
            if sender.name == self.name:
                asyncio.run(self.installer())

    def _should_skip(self):
        """Check if we should skip running installer"""
        # Skip during makemigrations, migrate, collectstatic, etc.
        skip_commands = [
            'makemigrations',
            'migrate',
            'collectstatic',
            'test',
            'flush',
            'loaddata',
            'dumpdata',
        ]

        # Check if any skip command is in sys.argv
        for cmd in skip_commands:
            if cmd in sys.argv:
                return True
        return False

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
