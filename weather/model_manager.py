from datetime import date
import pandas as pd
from weather.weather_data import WeatherDataRetriever, WeatherStatsCreator, get_latest_weather, WEATHER_URL
from weather.models import WxStats, CurrentWx


class DBInitializer:
    """
    Class that assists the initial loading of the database tables
    """
    @staticmethod
    def initialize_stats():
        yyc_stations_all_years = ({'station_id': 2205,
                                   'start_yr': 1881,
                                   'end_yr': 2012},
                                  {'station_id': 50430,
                                   'start_yr': 2012,
                                   'end_yr': 2020},
                                  )
        retriever = WeatherDataRetriever(WEATHER_URL)
        all_weather = retriever.create_weather_df(yyc_stations_all_years, drop_blanks=True)
        stats_creator = WeatherStatsCreator(all_weather)
        stats = stats_creator.create_weather_stats()
        WxStats.objects.all().delete()
        entries = []
        for entry in stats.T.to_dict().values():
            entries.append(WxStats(**entry))
        WxStats.objects.bulk_create(entries)


class ModelUpdator:
    """
    Object to assist with updating the
    """
    @staticmethod
    def set_current_weather():
        CurrentWx.objects.all().delete()
        yyc_current_station = ({'station_id': 50430,
                                'start_yr': date.today().year - 1,
                                'end_yr': date.today().year},
                               )
        latest_weather = get_latest_weather(yyc_current_station)
        entries = []
        for entry in latest_weather.T.to_dict().values():
            entries.append(CurrentWx(**entry))
        CurrentWx.objects.bulk_create(entries)


if __name__ == "__main__":

    latest = pd.read_csv("C:/Users/Jason/Documents/_Projects/2020-10 weather web app/latest_weather - Copy.csv")
    latest['date'] = pd.to_datetime(latest.date)
    latest.set_index("date", inplace=True)
    print(latest.info())

    weather_stats = pd.read_csv(
        "C:/Users/Jason/Documents/_Projects/2020-10 weather web app/weather_stats - Copy.csv")
    weather_stats['last_date'] = pd.to_datetime(weather_stats.last_date)
    weather_stats.set_index("month-day", inplace=True)
    print(weather_stats.info())

    DBInitializer().initialize_stats()
    stat_record = WxStats.objects.filter(month_day__exact="08-01")
    print("Stats for Aug 1:\n", stat_record)
    num_records = WxStats.objects.count()
    print("stats item count: ", num_records)
