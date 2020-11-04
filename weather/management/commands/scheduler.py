from apscheduler.schedulers.blocking import BlockingScheduler
from weather.model_manager import set_stats, update_weather_tables
from django.core.management.base import BaseCommand
import logging

logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def handle(self, *args, **options):
        # for background tasks
        scheduler = BlockingScheduler()

        # Run only once to initialize stats
        # scheduler.add_job(set_stats, 'cron', year=2020, month=11, day=4, hour=23, timezone='UTC')

        # Run this once per day to speed up responses
        scheduler.add_job(update_weather_tables, 'cron', hour=10, timezone='UTC')

        scheduler.start()
