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
    pass
