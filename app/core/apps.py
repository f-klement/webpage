from django.apps import AppConfig
import logging
from core.utils import start_scheduler

class CoreConfig(AppConfig):
    name = 'core'

    def ready(self):
        # Start the APScheduler when the app is ready.
        try:
            start_scheduler()
        except Exception as e:
            logging.error("Failed to start scheduler: %s", e)