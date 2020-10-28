from django.shortcuts import render
from bokeh.embed import components

from weather.trend_plot_builder import TrendPlotBuilder
from pathlib import Path

from weather.model_manager import set_stats, set_current_weather

# Create your views here.


def homepage(request):

    data_file = Path(__file__).resolve().parent.joinpath("data", "2015_weather.csv")
    builder = TrendPlotBuilder(data_file, smoothed=False)
    plot = builder.get_plot()
    script, div = components(plot)

    set_stats(from_api=False)
    set_current_weather(from_api=False)

    return render(request, "weather/base.html", {'script': script, 'div': div})
