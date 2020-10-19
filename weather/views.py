from django.shortcuts import render
from bokeh.embed import components

from .trend_plot_builder import TrendPlotBuilder
from pathlib import Path


# Create your views here.


def homepage(request):

    data_file_path = Path(__file__).resolve().parent.joinpath("data", "2015_weather.csv")
    builder = TrendPlotBuilder(data_file_path)
    plot_and_controls = builder.build_trend_plot()

    script, div = components(plot_and_controls)

    return render(request, "weather/base.html", {'script': script, 'div': div})
