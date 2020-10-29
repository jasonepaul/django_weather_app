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
    return latest_weather


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
    # update_weather_tables()
    return plot_df


def update_weather_tables():
    print("calling set_current_weather() from update_weather_tables()")
    current_wx_df = set_current_weather(from_api=True)
    current_wx_df = current_wx_df.dropna()
    for index, row in current_wx_df.iterrows():
        d, min_temp, max_temp, month_day = row['date'], row['min_temp'], row['max_temp'], row['month_day']
        rec = WxStats.objects.get(month_day=month_day)
        if d <= rec.last_date:
            print("continued")
            continue
        print("At least one record in WxStats is being changed")
        if min_temp < rec.record_min_temp:
            rec.record_min_temp = min_temp
        if max_temp > rec.record_max_tempp:
            rec.record_max_temp = max_temp
        new_stats_count = rec.stats_count + 1
        rec.avg_min_temp = (rec.avg_min_temp * rec.stats_count + min_temp) / new_stats_count
        rec.avg_max_temp = (rec.avg_max_temp * rec.stats_count + max_temp) / new_stats_count
        rec.stats_count = new_stats_count
        rec.save()




if __name__ == '__main__':
    df = table_to_df(CurrentWx)
