from django.shortcuts import render
from bokeh.plotting import figure
from bokeh.embed import components
from . import plot_trend


# Create your views here.


def homepage(request):

    x = [1, 2, 3, 4, 5]
    y = [1, 2, 3, 4, 5]

    plot = figure(title='Line Graph', plot_width=600, plot_height=400)

    plot.line(x, y, line_width=2)

    script, div = components(plot)

    return render(request, "weather/base.html", {'script': script, 'div': div})
