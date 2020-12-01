import datetime
import pandas as pd
from bokeh.models import ColumnDataSource, DataRange1d, HoverTool, Legend
from bokeh.palettes import BuGn4
from bokeh.plotting import figure
from weather.model_manager import get_plot_df


class TrendPlotBuilder:

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
        self.weather_df = get_plot_df(self.smoothed)

    def process_dataset(self):
        df = self.weather_df
        df['date'] = pd.to_datetime(df.date)
        df['left'] = df.date - datetime.timedelta(days=0.5)
        df['right'] = df.date + datetime.timedelta(days=0.5)
        df = df.set_index(['date'])
        self.source = ColumnDataSource(data=df)

    def make_plot(self):
        self.plot = figure(x_axis_type="datetime", tools='', sizing_mode='scale_width',
                           max_width=650, toolbar_location=None)
        r1 = self.plot.quad(top='record_max_temp', bottom='record_min_temp', left='left', right='right',
                            color=BuGn4[2], source=self.source)
        r2 = self.plot.quad(top='avg_max_temp', bottom='avg_min_temp', left='left', right='right',
                            color=BuGn4[1], source=self.source)
        r3 = self.plot.quad(top='max_temp', bottom='min_temp', left='left', right='right',
                            color=BuGn4[0], alpha=0.7, line_color="black", source=self.source)
        legend = Legend(items=[("Record", [r1]), ("Average", [r2]), ("Actual", [r3]), ],
                        location="center", orientation="horizontal", label_text_font_size="7pt",
                        border_line_color="lightgrey", label_standoff=3, spacing=10, padding=5)
        self.plot.add_layout(legend, 'below')
        # hover tool
        hover_tool = HoverTool(tooltips=[('Actuals', ''), ('date', '@date{%a %b %d}'),
                                         ('min', '@min_temp{0.0}\xb0C'),
                                         ('max', '@max_temp{0.0}\xb0C')],
                               formatters={'@date': 'datetime'},
                               renderers=[r3],
                               mode='vline')
        self.plot.add_tools(hover_tool)
        # attributes
        self.plot.xaxis.axis_label = "Date"
        self.plot.yaxis.axis_label = "Temperature Range Min-Max (\xb0C)"
        self.plot.axis.axis_label_text_font_style = "normal"
        self.plot.x_range = DataRange1d(range_padding=0.0)
        self.plot.grid.grid_line_alpha = 1.0

    def get_plot(self):
        return self.plot
