from django.apps import AppConfig


class MainConfig(AppConfig):
    name = 'main'

    def ready(self):
        # Import the signal receiver to patch the Oracle session
        # This ensures that the session is patched when the app is ready
        from . import oracle_init
