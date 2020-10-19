import datetime
import pandas as pd
from scipy.signal import savgol_filter
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, DataRange1d, Select
from bokeh.palettes import Blues4
from bokeh.plotting import figure


class TrendPlotBuilder:

    STATISTICS = ['record_min_temp', 'actual_min_temp', 'average_min_temp',
                  'average_max_temp', 'actual_max_temp', 'record_max_temp']

    def __init__(self, file_path):
        self.data_file = file_path
        self.city = 'Austin'
        self.distribution = 'Discrete'
        self.cities = {
            'Austin': {
                'airport': 'AUS',
                'title': 'Austin, TX',
            },
            'Boston': {
                'airport': 'BOS',
                'title': 'Boston, MA',
            },
            'Seattle': {
                'airport': 'SEA',
                'title': 'Seattle, WA',
            }
        }
        self.city_select = None
        self.distribution_select = None
        self.weather_df = None
        self.source = None  # a ColumnDataSource
        self.plot = None  # a Figure object

    def build_trend_plot(self):
        self.city_select = Select(value=self.city, title='City', options=sorted(self.cities.keys()))
        self.distribution_select = Select(value=self.distribution, title='Distribution',
                                          options=['Discrete', 'Smoothed'])

        self.weather_df = pd.read_csv(self.data_file)
        self.source = self.process_dataset(self.cities[self.city]['airport'], self.distribution)
        self.make_plot()

        self.city_select.on_change('value', self.update_plot)
        self.distribution_select.on_change('value', self.update_plot)

        controls = column(self.city_select, self.distribution_select)
        plot_and_controls = row(self.plot, controls)

        return plot_and_controls

    def process_dataset(self, name, distribution):
        df = self.weather_df[self.weather_df.airport == name].copy()
        del df['airport']
        df['date'] = pd.to_datetime(df.date)
        df['left'] = df.date - datetime.timedelta(days=0.5)
        df['right'] = df.date + datetime.timedelta(days=0.5)
        df = df.set_index(['date'])
        df.sort_index(inplace=True)
        if distribution == 'Smoothed':
            window, order = 51, 3
            for key in self.STATISTICS:
                df[key] = savgol_filter(df[key], window, order)
        return ColumnDataSource(data=df)

    def make_plot(self):
        self.plot = figure(x_axis_type="datetime", plot_width=800, tools="", toolbar_location=None)
        self.plot.title.text = "Weather data for " + self.cities[self.city]['title']

        self.plot.quad(top='record_max_temp', bottom='record_min_temp', left='left', right='right',
                       color=Blues4[2], source=self.source, legend_label="Record")
        self.plot.quad(top='average_max_temp', bottom='average_min_temp', left='left', right='right',
                       color=Blues4[1], source=self.source, legend_label="Average")
        self.plot.quad(top='actual_max_temp', bottom='actual_min_temp', left='left', right='right',
                       color=Blues4[0], alpha=0.5, line_color="black", source=self.source, legend_label="Actual")

        # attributes
        self.plot.xaxis.axis_label = "Date/Time"
        self.plot.yaxis.axis_label = "Temperature (F)"
        self.plot.axis.axis_label_text_font_style = "bold"
        self.plot.x_range = DataRange1d(range_padding=0.0)
        self.plot.grid.grid_line_alpha = 0.3

    def update_plot(self, attr, old, new):
        city = self.city_select.value
        self.plot.title.text = "Weather data for " + self.cities[city]['title']
        src = self.process_dataset(self.cities[city]['airport'], self.distribution_select.value)
        self.source.data.update(src.data)
