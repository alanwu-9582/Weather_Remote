import pandas as pd

from lib.weatherHelper import *

class AlertDataManager:
    def __init__(self, api_key):
        self.api_key = api_key
        self.alert_data = None

    def updateAlertData(self):
        data = pd.read_json(ALERT_URL.format(key=self.api_key))
        self.alert_data = pd.DataFrame(data["records"]["location"])

        return self.alert_data
    
    def getAlertLocations(self):
        if self.alert_data is None:
            self.updateAlertData()

        alert_locations = self.alert_data[self.alert_data["hazardConditions"].apply(lambda x: len(x["hazards"]) > 0)]
        return alert_locations
        