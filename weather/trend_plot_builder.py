import datetime
import pandas as pd
from scipy.signal import savgol_filter
from bokeh.models import ColumnDataSource, DataRange1d, HoverTool, DatetimeTickFormatter
from bokeh.palettes import BuGn4
from bokeh.plotting import figure
from weather.model_manager import get_plot_df


class TrendPlotBuilder:

    STATISTICS = ['avg_min_temp', 'avg_max_temp']

    def __init__(self, smoothed=False):
        self.weather_df = None
        self.source = None  # a ColumnDataSource object
        self.plot = None  # a Figure object
        self.smoothed = smoothed
        self.build_trend_plot()

    def build_trend_plot(self):

        self.create_df_from_db()
        self.process_dataset()
        self.make_plot()

    def create_df_from_db(self):
        self.weather_df = get_plot_df()

    def process_dataset(self):
        df = self.weather_df
        df['date'] = pd.to_datetime(df.date)
        df['left'] = df.date - datetime.timedelta(days=0.5)
        df['right'] = df.date + datetime.timedelta(days=0.5)
        df = df.set_index(['date'])
        df.sort_index(inplace=True)
        if self.smoothed:
            window, order = 31, 2
            for key in TrendPlotBuilder.STATISTICS:
                df[key] = savgol_filter(df[key], window, order)
        self.source = ColumnDataSource(data=df)

    def make_plot(self):
        self.plot = figure(x_axis_type="datetime", plot_width=650,
                           tools='pan, reset, box_zoom',)
        self.plot.xaxis.formatter = DatetimeTickFormatter(days=["%b %d"])
        self.plot.title.text = "Temperature Trend for Calgary (YYC Airport)"
        self.plot.title.align = "center"
        self.plot.title.text_font_size = "16px"
        self.plot.quad(top='record_max_temp', bottom='record_min_temp', left='left', right='right',
                       color=BuGn4[2], source=self.source, legend_label="Record")
        self.plot.quad(top='avg_max_temp', bottom='avg_min_temp', left='left', right='right',
                       color=BuGn4[1], source=self.source, legend_label="Average")
        r = self.plot.quad(top='max_temp', bottom='min_temp', left='left', right='right',
                           color=BuGn4[0], alpha=0.7, line_color="black", source=self.source, legend_label="Actual")

        self.plot.legend.orientation = "horizontal"
        # hover tool
        hover_tool = HoverTool(tooltips=[('Actuals', ''), ('date', '@date{%a %b %d}'),
                                         ('min', '@min_temp{0.0}\xb0C'),
                                         ('max', '@max_temp{0.0}\xb0C')],
                               formatters={'@date': 'datetime'},
                               renderers=[r],
                               mode='vline')
        self.plot.add_tools(hover_tool)
        # attributes
        self.plot.xaxis.axis_label = "Date"
        self.plot.yaxis.axis_label = "Temperature (\xb0C)"
        self.plot.axis.axis_label_text_font_style = "bold"
        self.plot.x_range = DataRange1d(range_padding=0.0)
        self.plot.grid.grid_line_alpha = 1.0

    def get_plot(self):
        return self.plot
