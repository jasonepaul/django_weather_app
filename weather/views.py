from django.shortcuts import render
from bokeh.embed import components
import pandas as pd

from weather.trend_plot_builder import TrendPlotBuilder
from pathlib import Path

from datetime import date
from weather.weather_data import WeatherDataRetriever, WeatherStatsCreator, get_latest_weather, WEATHER_URL
from weather.models import WxStats, CurrentWx

# Create your views here.


def get_wx_stats():
    weather_stats = pd.read_csv(
        "C:/Users/Jason/Documents/_Projects/2020-10 weather web app/weather_stats - Copy.csv")
    weather_stats['last_date'] = pd.to_datetime(weather_stats.last_date)
    # weather_stats.set_index("month_day", inplace=True)
    # print(weather_stats.info())
    return weather_stats


def get_latest_wx():
    latest = pd.read_csv("C:/Users/Jason/Documents/_Projects/2020-10 weather web app/latest_weather - Copy.csv")
    latest['date'] = pd.to_datetime(latest.date)
    # latest.set_index("date", inplace=True)
    # print(latest.info())
    return latest


def set_stats():
    # yyc_stations_all_years = ({'station_id': 2205,
    #                            'start_yr': 1881,
    #                            'end_yr': 2012},
    #                           {'station_id': 50430,
    #                            'start_yr': 2012,
    #                            'end_yr': 2020},
    #                           )
    # retriever = WeatherDataRetriever(WEATHER_URL)
    # all_weather = retriever.create_weather_df(yyc_stations_all_years, drop_blanks=True)
    # stats_creator = WeatherStatsCreator(all_weather)
    # stats = stats_creator.create_weather_stats()
    stats = get_wx_stats()

    WxStats.objects.all().delete()
    print("Number of entries: ", WxStats.objects.all().count())
    entries = []
    for entry in stats.T.to_dict().values():
        entries.append(WxStats(**entry))
        print(entry)
    WxStats.objects.bulk_create(entries)
    num_records = WxStats.objects.count()
    print("stats item count: ", num_records)
    stat_record = WxStats.objects.get(month_day="08-01")
    print("Stats for Aug 1:\n", stat_record.avg_max_temp)
    # for record in stat_record:
    #     print("Stats for Aug 1:\n", record.month_day)



def set_current_weather():
    # CurrentWx.objects.all().delete()
    # yyc_current_station = ({'station_id': 50430,
    #                         'start_yr': date.today().year - 1,
    #                         'end_yr': date.today().year},
    #                        )
    # latest_weather = get_latest_weather(yyc_current_station)
    latest_weather = get_latest_wx()

    CurrentWx.objects.all().delete()
    entries = []
    for entry in latest_weather.T.to_dict().values():
        entries.append(CurrentWx(**entry))
    CurrentWx.objects.bulk_create(entries)

    current_wx_record = CurrentWx.objects.filter(month_day__exact="08-01")
    print("Current weather for Aug 1:\n", current_wx_record)
    num_records = CurrentWx.objects.count()
    print("Current weather item count: ", num_records)


def homepage(request):

    data_file = Path(__file__).resolve().parent.joinpath("data", "2015_weather.csv")
    builder = TrendPlotBuilder(data_file, smoothed=False)
    plot = builder.get_plot()
    script, div = components(plot)

    set_stats()
    # set_current_weather()

    return render(request, "weather/base.html", {'script': script, 'div': div})
