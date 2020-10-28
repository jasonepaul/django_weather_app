from datetime import date
import pandas as pd
from weather.weather_data import WeatherDataRetriever, WeatherStatsCreator, \
    get_latest_weather, WEATHER_URL, get_wx_stats_from_csv, get_latest_wx_from_csv
from weather.models import WxStats, CurrentWx


def set_stats(from_api=True):
    print("\nPopulating the WxStats db table\n")
    if from_api:
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
    else:
        stats = get_wx_stats_from_csv()

    WxStats.objects.all().delete()
    entries = []
    for entry in stats.T.to_dict().values():
        entries.append(WxStats(**entry))
    WxStats.objects.bulk_create(entries)


def set_current_weather(from_api=True):
    print("\nPopulating the CurrentWx db table\n")
    if from_api:
        yyc_current_station = ({'station_id': 50430,
                                'start_yr': date.today().year - 1,
                                'end_yr': date.today().year},
                               )
        latest_weather = get_latest_weather(yyc_current_station)
    else:
        latest_weather = get_latest_wx_from_csv()

    CurrentWx.objects.all().delete()
    entries = []
    for entry in latest_weather.T.to_dict().values():
        entry = {k: v for k, v in entry.items() if not pd.isnull(v)}  # don't include blank fields
        entries.append(CurrentWx(**entry))
    CurrentWx.objects.bulk_create(entries)


def table_to_df(table):
    table_list = list(table.objects.all().values())
    df = pd.DataFrame(table_list)
    return df


def get_plot_df():
    if not CurrentWx.objects.exists():
        set_current_weather(from_api=False)
    if not WxStats.objects.exists():
        set_stats(from_api=False)
    current_wx = table_to_df(CurrentWx)
    wx_stats = table_to_df(WxStats)
    wx_stats = wx_stats.drop(columns=['last_date', 'stats_count'])
    plot_df = pd.merge(current_wx, wx_stats, how='inner', on=['month_day'])
    plot_df = plot_df.drop(columns=['month_day'])
    print(plot_df.info())
    return plot_df


if __name__ == "__main__":
    pass
