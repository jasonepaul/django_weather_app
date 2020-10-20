import datetime
import pandas as pd
from scipy.signal import savgol_filter
from bokeh.models import ColumnDataSource, DataRange1d
from bokeh.palettes import BuGn4
from bokeh.plotting import figure


class TrendPlotBuilder:

    STATISTICS = ['record_min_temp', 'actual_min_temp', 'average_min_temp',
                  'average_max_temp', 'actual_max_temp', 'record_max_temp']

    def __init__(self, file_path, smoothed=False):
        self.data_file = file_path
        self.weather_df = None
        self.source = None  # a ColumnDataSource
        self.plot = None  # a Figure object
        self.smoothed = smoothed

    def build_trend_plot(self):

        self.create_df_from_csv()
        self.process_dataset()
        self.make_plot()

        return self.plot

    def create_df_from_csv(self):
        self.weather_df = pd.read_csv(self.data_file)

    def process_dataset(self):
        df = self.weather_df
        df['date'] = pd.to_datetime(df.date)
        df['left'] = df.date - datetime.timedelta(days=0.5)
        df['right'] = df.date + datetime.timedelta(days=0.5)
        df = df.set_index(['date'])
        df.sort_index(inplace=True)
        # df = df[:]
        if self.smoothed:
            window, order = 51, 3
            for key in self.STATISTICS:
                df[key] = savgol_filter(df[key], window, order)
        self.source = ColumnDataSource(data=df)

    def make_plot(self):
        self.plot = figure(x_axis_type="datetime", plot_width=800, tools="", toolbar_location=None)
        self.plot.title.text = "Weather Data for Seattle"
        self.plot.quad(top='record_max_temp', bottom='record_min_temp', left='left', right='right',
                       color=BuGn4[2], source=self.source, legend_label="Record")
        self.plot.quad(top='average_max_temp', bottom='average_min_temp', left='left', right='right',
                       color=BuGn4[1], source=self.source, legend_label="Average")
        self.plot.quad(top='actual_max_temp', bottom='actual_min_temp', left='left', right='right',
                       color=BuGn4[0], alpha=0.7, line_color="black", source=self.source, legend_label="Actual")
        # attributes
        self.plot.xaxis.axis_label = "Date"
        self.plot.yaxis.axis_label = "Temperature (F)"
        self.plot.axis.axis_label_text_font_style = "bold"
        self.plot.x_range = DataRange1d(range_padding=0.0)
        self.plot.grid.grid_line_alpha = 0.5
