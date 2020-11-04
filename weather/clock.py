from apscheduler.schedulers.blocking import BlockingScheduler
from weather.model_manager import set_stats, update_weather_tables

# for background tasts
schedule = BlockingScheduler()


schedule.add_job(set_stats, 'cron', year=2020, month=11, day=4, hour=19, timezone='UTC')
schedule.add_job(update_weather_tables, 'cron', hour=10, timezone='UTC')

schedule.start()
