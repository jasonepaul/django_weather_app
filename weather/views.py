from django.shortcuts import render
from bokeh.embed import components

from .trend_plot_builder import TrendPlotBuilder
from pathlib import Path


# Create your views here.


def homepage(request):

    data_file = Path(__file__).resolve().parent.joinpath("data", "2015_weather.csv")
    builder = TrendPlotBuilder(data_file, smoothed=False)
    plot = builder.get_plot()
    script, div = components(plot)

    return render(request, "weather/base.html", {'script': script, 'div': div})
