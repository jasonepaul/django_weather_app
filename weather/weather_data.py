import pandas as pd
from datetime import date, timedelta


class WeatherDataRetriever:
    """
    Retrieves weather data from the Canada climate data API and creates a DataFrame.
    The resulting DataFrame has these columns:
        date/time (index)
        min temp (c)
        max temp (c)
    """

    def __init__(self):
        self.weather_api_url = 'https://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv' \
                               '&stationID={station}&Year={year}&Month={month}&timeframe={time_int}' \
                               '&submit=Download+Data'

    def create_all_weather_df(self):
        """
        Returns a cleaned DataFrame of Calgary YYC min and max temperatures for all years
        """
        weather_df = self._get_all_weather_data()
        weather_df = self._clean_data(weather_df)
        return weather_df

    def create_weather_df(self, station, year):
        """
        Returns a cleaned DataFrame of min and max temperatures for a given year
        """
        weather_df = self._call_api(station, year)
        return self._clean_data(weather_df, drop_blanks=False)

    def _get_all_weather_data(self) -> pd.DataFrame:
        """
        Helper function for retrieving all the Calgary YYC data from the API and concatenating the resulting dataframes
        @return: weather dataframe
        """
        df_list = []
        for yr in range(1881, 2013):
            df = self._call_api(2205, yr)
            df_list.append(df)
        for yr in range(2012, 2021):
            df = self._call_api(50430, yr)
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
        # replace the degree symbol in the column names
        weather_data.columns = [col.replace('\xb0', '') for col in weather_data.columns]
        return weather_data

    @staticmethod
    def _clean_data(weather_df, drop_blanks=True) -> pd.DataFrame:
        """
        Takes a DataFrame with weather data, extracts only columns needed, converts column names to lower case,
        drops NAs as appropriate, then sorts and returns the DataFrame
        """
        all_weather_cleaned = weather_df[['Min Temp (C)', 'Max Temp (C)']]
        all_weather_cleaned.columns = [col.lower() for col in all_weather_cleaned.columns]
        if drop_blanks:
            all_weather_cleaned.dropna(inplace=True)
        all_weather_cleaned.sort_index(inplace=True)
        return all_weather_cleaned

    @staticmethod
    def save_to_csv(df):
        """
        Save the dataframe to csv for review (for testing purposes only)
        """
        df.to_csv("C:/Users/Jason/Documents/_Projects/2020-10 yyc_weather web app/all_weather.csv")


class WeatherStatsCreator:
    """
    Class used to create the stats for the Weather_Stats model.
    """

    def __init__(self, weather_df):
        self.weather_df = weather_df  # DataFrame of entire history of daily min and max temperatures
                                      # weather_df must have columns: date/time, min temp (c), max temp (c)
        self._add_month_day()

    def _add_month_day(self):
        """
        Adds the month-day column to the DataFrame
        """
        month = self.weather_df.index.month.astype(str)
        month = month.map(lambda x: str(x) if len(x) == 2 else '0' + str(x))
        day = self.weather_df.index.day.astype(str)
        day = day.map(lambda x: str(x) if len(x) == 2 else '0' + str(x))
        self.weather_df['month-day'] = month + "-" + day

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
        weather_stats['last_date'] = month_day_series.index  # last date this day-of-year has temp data for
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

    @staticmethod
    def save_to_csv(df):
        """
        Save the dataframe to csv for review (for testing purposes only)
        """
        df.to_csv("C:/Users/Jason/Documents/_Projects/2020-10 yyc_weather web app/weather_stats.csv")


class CurrentWeatherDataRetriever:
    """
    Class used to create a DataFrame of latest weather min and max temperatures
    """


if __name__ == "__main__":
    retriever = WeatherDataRetriever()
    all_weather = retriever.create_all_weather_df()
    retriever.save_to_csv(all_weather)
    stats_creator = WeatherStatsCreator(all_weather)
    stats = stats_creator.create_weather_stats()
    stats_creator.save_to_csv(stats)
