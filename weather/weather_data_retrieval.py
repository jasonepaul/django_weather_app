import pandas as pd


class AllWeatherDataRetriever:

    def __init__(self):
        self.weather_api_url = """https://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv
                                  &stationID={station}&Year={year}&Month={month}&timeframe={time_int}
                                  &submit=Download+Data"""
        self.weather_df = pd.DataFrame()
        self.weather_stats_df = pd.DataFrame()

    def create_weather_df(self):
        weather_df = self._get_weather_data()
        weather_df_cleaned = self._clean_data(weather_df)
        self.weather_df = self._add_month_day(weather_df_cleaned)

    def _get_weather_data(self) -> pd.DataFrame:
        """
        Helper function for retrieving the data from the API and concatenating the resulting dataframes
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
    def _clean_data(weather_df) -> pd.DataFrame:
        all_weather_cleaned = weather_df[['Station Name', 'Month', 'Day', 'Min Temp (C)', 'Max Temp (C)']]
        all_weather_cleaned.columns = [col.lower() for col in all_weather_cleaned.columns]
        all_weather_cleaned.dropna(inplace=True).sort_index()
        return all_weather_cleaned

    @staticmethod
    def _add_month_day(weather_df) -> pd.DataFrame:
        month = weather_df.month.map(lambda x: str(x) if len(x) == 2 else '0' + str(x))
        day = weather_df.day.map(lambda x: str(x) if len(x) == 2 else '0' + str(x))
        weather_df['month-day'] = month + "-" + day
        return weather_df

    def create_weather_stats(self):
        month_day_series = self.weather_df.drop_duplicates(subset=['month-day'], keep='last')['month-day']
        weather_stats = pd.DataFrame()
        weather_stats['month-day'] = month_day_series
        weather_stats['last_date'] = month_day_series.index  # last date this day-of-year has temp data for
        weather_stats.set_index(['month-day'], inplace=True).sort_index(inplace=True)
        groupby = self.weather_df.groupby('month-day')[f'min temp (c)']
        weather_stats[f'record_min_temp'] = groupby.min()
        weather_stats[f'avg_min_temp'] = groupby.mean()
        groupby = self.weather_df.groupby('month-day')[f'max temp (c)']
        weather_stats[f'avg_max_temp'] = groupby.mean()
        weather_stats[f'record_max_temp'] = groupby.max()
        weather_stats[f'stats_count'] = groupby.count()
        self.weather_stats_df = weather_stats

    def save_to_csv(self):
        self.weather_df.to_csv("C:/Users/Jason/Documents/_Projects/2020-10 yyc_weather web app/all_yyc_weather.csv")
        self.weather_stats_df.to_csv("C:/Users/Jason/Documents/_Projects/2020-10 yyc_weather web app/weather_stats.csv")


class CurrentWeatherDataRetriever:
    pass
