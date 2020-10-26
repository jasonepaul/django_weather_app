import pandas as pd
from datetime import date, timedelta

WEATHER_URL = 'https://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv' \
              '&stationID={station}&Year={year}&Month={month}&timeframe={time_int}' \
              '&submit=Download+Data'


class WeatherDataRetriever:
    """
    Retrieves weather data from the Canada climate data API and creates a DataFrame.
    The resulting DataFrame has these columns:
        date/time (index)
        min temp (c)
        max temp (c)
    """

    def __init__(self, url):
        self.weather_api_url = url

    def create_weather_df(self, stations, drop_blanks):
        """
        Returns a cleaned DataFrame of min and max temperatures for all years
        """
        weather_df = self._get_weather_data(stations)
        weather_df = self._clean_data(weather_df, drop_blanks)
        weather_df = self._add_month_day(weather_df)
        return weather_df

    def _get_weather_data(self, stations) -> pd.DataFrame:
        """
        Helper function for retrieving all the data from the API and concatenating the resulting dataframes
        @return: weather dataframe
        """
        df_list = []
        for station in stations:
            for yr in range(station['start_yr'], station['end_yr'] + 1):
                df = self._call_api(station['station_id'], yr)
                df_list.append(df)
        return pd.concat(df_list)

    def _call_api(self, station, year, month=1, daily=True) -> pd.DataFrame:
        """
        Connects to API and retrieves the weather data
        @param station: station ID
        @param year: year of data
        @param month: month of data (required by API but does not do anything for our query)
        @param daily: boolean for whether data should be in daily format
        @return: weather dataframe
        """
        if daily:
            url = self.weather_api_url.format(station=station, year=year, month=month, time_int=2)
        else:
            url = self.weather_api_url.format(station=station, year=year, month=month, time_int=1)
        weather_data = pd.read_csv(url, index_col='Date/Time', parse_dates=True)
        return weather_data

    @staticmethod
    def _clean_data(weather_df, drop_blanks=True) -> pd.DataFrame:
        """
        Takes a DataFrame with weather data, extracts only columns needed, converts column names to lower case,
        drops NAs as appropriate, then sorts and returns the DataFrame
        """
        weather_df.columns = [col.replace('\xb0', '') for col in weather_df.columns]  # remove degree symbol
        weather_df = weather_df[['Min Temp (C)', 'Max Temp (C)']]
        weather_df.columns = [col.lower() for col in weather_df.columns]
        if drop_blanks:
            weather_df.dropna(inplace=True)
        weather_df.sort_index(inplace=True)
        return weather_df

    @staticmethod
    def _add_month_day(weather_df):
        """
        Adds the month-day column to the DataFrame
        """
        month = weather_df.index.month.astype(str)
        month = month.map(lambda x: str(x) if len(x) == 2 else '0' + str(x))
        day = weather_df.index.day.astype(str)
        day = day.map(lambda x: str(x) if len(x) == 2 else '0' + str(x))
        weather_df['month-day'] = month + "-" + day
        return weather_df


class WeatherStatsCreator:
    """
    Class used to create the stats for the Weather_Stats model.
    """

    def __init__(self, weather_df):
        self.weather_df = weather_df  # DataFrame of entire history of daily min and max temperatures
        # weather_df must have columns: date/time, min temp (c), max temp (c)

    def create_weather_stats(self):
        """
        Creates the weather stats DataFrame in two steps, first creating the template, then creating the stats.
        """
        weather_stats = self._create_template()
        weather_stats_df = self._compute_stats(weather_stats)
        return weather_stats_df

    def _create_template(self):
        """
        Helper that uses the weather_df as a starting point to put together the weather_stats_df
        """
        month_day_series = self.weather_df.drop_duplicates(subset=['month-day'], keep='last')['month-day']
        weather_stats = pd.DataFrame()
        weather_stats['month-day'] = month_day_series
        weather_stats['last_date'] = month_day_series.index  # last date this day-of-year has temperature data for
        weather_stats.set_index(['month-day'], inplace=True)
        weather_stats.sort_index(inplace=True)
        return weather_stats

    def _compute_stats(self, weather_stats):
        """
        Creates the temperature stats for each day of year (366 total):
            record minimum temperature
            average minimum temperature
            record maximum temperature
            average maximum temperature
        @param weather_stats: the weather stats template DataFrame
        @return: weather stats DataFrame
        """
        groupby = self.weather_df.groupby('month-day')[f'min temp (c)']
        weather_stats[f'record_min_temp'] = groupby.min()
        weather_stats[f'avg_min_temp'] = groupby.mean()
        groupby = self.weather_df.groupby('month-day')[f'max temp (c)']
        weather_stats[f'avg_max_temp'] = groupby.mean()
        weather_stats[f'record_max_temp'] = groupby.max()
        weather_stats[f'stats_count'] = groupby.count()
        return weather_stats


def get_latest_weather(stations, num_weeks=12):
    """
    Returns a DataFrame of min and max temperatures for the most recent num_weeks
    @param stations: weather station IDs
    @param num_weeks: number of weeks to show in the plot
    @return: DataFrame of min and max temperatures for the most recent num_weeks
    """
    ret = WeatherDataRetriever(WEATHER_URL)
    curr_weather = ret.create_weather_df(stations, drop_blanks=False)
    end = date.today() - timedelta(days=1)
    start = end - timedelta(days=(7 * num_weeks) - 1)
    most_recent = curr_weather[str(start):str(end)]
    return most_recent


if __name__ == "__main__":
    yyc_stations_all_years = ({'station_id': 2205,
                               'start_yr': 1881,
                               'end_yr': 2012},
                              {'station_id': 50430,
                               'start_yr': 2012,
                               'end_yr': 2020},
                              )
    retriever = WeatherDataRetriever(WEATHER_URL)
    all_weather = retriever.create_weather_df(yyc_stations_all_years, drop_blanks=True)
    all_weather.to_csv("C:/Users/Jason/Documents/_Projects/2020-10 weather web app/all_weather.csv")

    stats_creator = WeatherStatsCreator(all_weather)
    stats = stats_creator.create_weather_stats()
    stats.to_csv("C:/Users/Jason/Documents/_Projects/2020-10 weather web app/weather_stats.csv")

    yyc_current_station = ({'station_id': 50430,
                            'start_yr': date.today().year - 1,
                            'end_yr': date.today().year},
                           )
    latest_weather = get_latest_weather(yyc_current_station)
    latest_weather.to_csv("C:/Users/Jason/Documents/_Projects/2020-10 weather web app/latest_weather.csv")
    latest_weather.info()
    latest_weather.head()
    latest_weather.tail()
