from django.shortcuts import render
from bokeh.embed import components

from weather.trend_plot_builder import TrendPlotBuilder

from weather.model_manager import get_plot_df

# Create your views here.


def homepage(request):

    builder = TrendPlotBuilder(smoothed=True)
    plot = builder.get_plot()
    script, div = components(plot)

    return render(request, "weather/base.html", {'script': script, 'div': div})
