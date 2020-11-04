from apscheduler.schedulers.background import BackgroundScheduler
from weather.model_manager import set_stats, update_weather_tables
from django.core.management.base import BaseCommand
from apscheduler.triggers.cron import CronTrigger
import logging

logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)


def timed_job():
    print('timed_job just run.')


class Command(BaseCommand):

    def handle(self, *args, **options):
        # for background tasks
        scheduler = BackgroundScheduler()

        scheduler.add_job(
            timed_job,
            trigger=CronTrigger(second="*/10"),  # Every 10 seconds
            id="my_job",  # The `id` assigned to each job MUST be unique
            max_instances=3,
            replace_existing=True,
        )
        logger.info("Added job timed_job.")

        scheduler.add_job(set_stats, 'cron', year=2020, month=11, day=4, hour=24, timezone='UTC')
        scheduler.add_job(update_weather_tables, 'cron', hour=10, timezone='UTC')
        logger.info("Added job set_stats and update_weather_tables.")

        scheduler.start()
