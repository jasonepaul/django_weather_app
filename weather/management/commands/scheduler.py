from apscheduler.schedulers.background import BackgroundScheduler
from weather.model_manager import set_stats, update_weather_tables
from django.core.management.base import BaseCommand


# for background tasts
schedule = BackgroundScheduler()


schedule.add_job(set_stats, 'cron', year=2020, month=11, day=4, hour=22, timezone='UTC')
schedule.add_job(update_weather_tables, 'cron', hour=10, timezone='UTC')


@schedule.scheduled_job('interval', minutes=1)
def timed_job():
    print('This job is run every minute.')


class Command(BaseCommand):

    def handle(self, *args, **options):
        schedule.start()
