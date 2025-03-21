import pandas as pd

from lib.weatherHelper import *

class ForecastDataManager:
    def __init__(self, api_key):
        self.api_key = api_key
        self.forecast_data = None

    def updateForecastData(self):
        data = pd.read_json(FORECAST_URL.format(key=self.api_key))
        self.forecast_data = pd.DataFrame(data["records"]["location"])

        return self.forecast_data
    
    def getForecast(self, location):
        if self.forecast_data is None:
            self.updateForecastData()

        forecast = self.forecast_data[self.forecast_data["locationName"] == location]
        elements = pd.DataFrame(forecast["weatherElement"].iloc[0])
    
        def get_element_df(elements, name):
            match = elements.loc[elements["elementName"] == name, "time"]
            return pd.DataFrame(match.values[0]) if not match.empty else pd.DataFrame()

        wx_datas = get_element_df(elements, "Wx")
        pop_datas = get_element_df(elements, "PoP")
        minT_datas = get_element_df(elements, "MinT")
        maxT_datas = get_element_df(elements, "MaxT")
        ci_datas = get_element_df(elements, "CI")

        forecast_report = [
            {
                "start": wx_datas["startTime"].iloc[i],
                "weather": wx_datas["parameter"].iloc[i]["parameterName"],
                "weather_code": wx_datas["parameter"].iloc[i]["parameterValue"],
                "min_temp": minT_datas["parameter"].iloc[i]["parameterName"],
                "max_temp": maxT_datas["parameter"].iloc[i]["parameterName"],
                "pop": pop_datas["parameter"].iloc[i]["parameterName"],
                "feel": ci_datas["parameter"].iloc[i]["parameterName"]
            } for i in range(len(wx_datas))
        ]

        return pd.DataFrame(forecast_report)
    

    def getLocations(self):
        if self.forecast_data is None:
            self.updateForecastData()

        return self.forecast_data["locationName"].tolist()
    