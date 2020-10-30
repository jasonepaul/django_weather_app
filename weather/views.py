from django.shortcuts import render
from bokeh.embed import components

from weather.trend_plot_builder import TrendPlotBuilder
from weather.models import WxStats


# Create your views here.


def homepage(request):

    builder = TrendPlotBuilder(smoothed=True)
    plot = builder.get_plot()
    script, div = components(plot)
    max_years = WxStats.objects.order_by("-stats_count")[0].stats_count
    context = {'script': script,
               'div': div,
               'max_years': max_years}

    return render(request, "weather/base.html", context=context)
