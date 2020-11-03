from datetime import date
import pandas as pd
from weather.models import WxStats, CurrentWx, Info
from weather.weather_data import WeatherDataRetriever, WeatherStatsCreator, \
    get_latest_weather, WEATHER_URL, get_wx_stats_from_csv, get_latest_wx_from_csv


def set_stats(from_api=True):
    """
    Initializes the db table for weather stats
    @param from_api: Whether to pull the data from the online API of from a csv file
    """
    if from_api:
        yyc_stations_all_years = ({'station_id': 2205, 'start_yr': 1881, 'end_yr': 2012},
                                  {'station_id': 50430, 'start_yr': 2012, 'end_yr': 2020},)
        retriever = WeatherDataRetriever(WEATHER_URL)
        all_weather = retriever.create_weather_df(yyc_stations_all_years, drop_blanks=True)
        stats = WeatherStatsCreator(all_weather).create_weather_stats()
    else:
        stats = get_wx_stats_from_csv()
    WxStats.objects.all().delete()
    entries = []
    for entry in stats.T.to_dict().values():
        entries.append(WxStats(**entry))
    WxStats.objects.bulk_create(entries)


def set_current_weather(from_api=True):
    """
    Initializes the db table for latest weeks of weather (min and max daily temperature)
    @param from_api: Whether to pull the data from the online API of from a csv file
    @return: DataFrame for the latest weather
    """
    if from_api:
        yyc_current_station = ({'station_id': 50430, 'start_yr': date.today().year - 1,
                                'end_yr': date.today().year},)
        latest_weather = get_latest_weather(yyc_current_station)
    else:
        latest_weather = get_latest_wx_from_csv()
    CurrentWx.objects.all().delete()
    entries = []
    for entry in latest_weather.T.to_dict().values():
        entry = {k: v for k, v in entry.items() if not pd.isnull(v)}  # don't include blank fields
        entries.append(CurrentWx(**entry))
    CurrentWx.objects.bulk_create(entries)
    return latest_weather


def set_info():
    """
    Initialize the info table with a single record that keeps track of the date
    of last db table data retrieval
    """
    Info.objects.all().delete()
    Info(last_update=date.today()).save()


def table_to_df(table):
    """
    Returns a db table as a dataframe
    """
    table_list = list(table.objects.all().values())
    df = pd.DataFrame(table_list)
    return df


def update_last_db_access_date():
    info_rec = Info.objects.get(pk=1)
    info_rec.last_update = date.today()
    info_rec.save()


def date_db_last_updated():
    return Info.objects.get(pk=1).last_update


def update_weather_tables():
    current_wx_df = set_current_weather(from_api=True)
    current_wx_df = current_wx_df.dropna()
    for index, row in current_wx_df.iterrows():
        d, min_temp, max_temp, month_day = row['date'], row['min_temp'], row['max_temp'], row['month_day']
        rec = WxStats.objects.get(month_day=month_day)
        if d <= rec.last_date:
            continue
        if min_temp < rec.record_min_temp:
            rec.record_min_temp = min_temp
        if max_temp > rec.record_max_temp:
            rec.record_max_temp = max_temp
        new_stats_count = rec.stats_count + 1
        rec.avg_min_temp = (rec.avg_min_temp * rec.stats_count + min_temp) / new_stats_count
        rec.avg_max_temp = (rec.avg_max_temp * rec.stats_count + max_temp) / new_stats_count
        rec.stats_count = new_stats_count
        rec.last_date = d
        rec.save()
    update_last_db_access_date()


def initialize_db():
    """
    Initializes all database tables on first time access to the website.
    """
    if WxStats.objects.exists() and CurrentWx.objects.exists() and Info.objects.exists():
        print("DB Tables already populated!")
        return
    set_stats(from_api=True)
    set_current_weather(from_api=True)
    set_info()
    print("DB Tables initialized!")


def get_plot_df():
    """
    Returns a dataframe suitable for the Bokeh plot
    """
    if date_db_last_updated() < date.today():  # typically only true on the first server access of any given day
        update_weather_tables()  # todo replace this call with background task
    current_wx = table_to_df(CurrentWx)
    wx_stats = table_to_df(WxStats)
    wx_stats = wx_stats.drop(columns=['last_date', 'stats_count'])
    plot_df = pd.merge(current_wx, wx_stats, how='inner', on=['month_day'])
    plot_df = plot_df.drop(columns=['month_day'])
    return plot_df
