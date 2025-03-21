import threading
import time
import schedule
import streamlit as st
from streamlit_folium import folium_static
from constants import API_KEY
from lib.weatherHelper import get_weather_icon
from lib.weatherData import WeatherDataManager
from lib.forecastData import ForecastDataManager
from lib.alertData import AlertDataManager

# 整合 schedule + 顯示最後更新時間
class website:
    def __init__(self):
        self.weather_data_manager = WeatherDataManager(API_KEY)
        self.forecast_data_manager = ForecastDataManager(API_KEY)
        self.alert_data_manager = AlertDataManager(API_KEY)

        self.last_alert_update = None  # 儲存最後更新時間
        self.start_scheduler()

        self.initUI()

    def run(self):
        self.connectEvent()

    def initUI(self):
        st.title("即時天氣監測")

        st.markdown("### 即時天氣資訊")
        self.weather_alert = st.empty()
        self.updateAlert()

        st.markdown("### 天氣資料查詢")
        weather_cols = st.columns([4, 1, 1])

        with weather_cols[0]:
            self.weather_selection = st.selectbox("選擇資料來源", ["Station", "Now"])

        with weather_cols[1]:
            self.make_space(1.7)
            self.update_map = st.button("顯示地圖")

        with weather_cols[2]:
            self.make_space(2)
            self.only_wind = st.checkbox("只顯示風向")

        forecast_cols = st.columns([4, 1])

        with forecast_cols[0]:
            locations = self.forecast_data_manager.getLocations()
            self.forecast_selection = st.selectbox("選擇查詢地區", locations)

        with forecast_cols[1]:
            self.make_space(1.7)
            self.display_forecast = st.button("查詢天氣預報")

        st.markdown("> 資料來源：[中央氣象署](https://opendata.cwa.gov.tw/index)")

    def connectEvent(self):
        if self.update_map:
            folium_static(self.weather_data_manager.getMap(self.weather_selection, only_wind=self.only_wind, update=True))

        if self.display_forecast:
            self.displayForecast()

    def displayForecast(self):
        st.markdown(f"## {self.forecast_selection} 36 小時天氣預報")
        forecast_report = self.forecast_data_manager.getForecast(self.forecast_selection)

        display_cols = st.columns(3)
        for i, col in enumerate(display_cols):
            with col:
                data = forecast_report.iloc[i]
                icon = get_weather_icon(data["weather_code"])
                st.subheader(data["start"])
                st.markdown(f"{icon} **{data['weather']}**")
                st.write(f"🌡️ {data['min_temp']}°C ~ {data['max_temp']}°C")
                st.write(f"💧 降雨機率：{data['pop']}%")
                st.write(f"🧣 體感：{data['feel']}")

    def updateAlert(self):
        self.alert_data_manager.updateAlertData()
        self.last_alert_update = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        alert_locations = self.alert_data_manager.getAlertLocations()

        if alert_locations.empty:
            st.markdown("✅ 目前各地無天氣警特報。")
        else:
            md = "#### ⚠️ 天氣警特報\n"

            for _, location in alert_locations.iterrows():
                md += f"\n- **{location['locationName']}**\n"
                for hazard in location["hazardConditions"]["hazards"]:
                    info = hazard["info"]
                    time_range = hazard["validTime"]
                    md += f"  - **現象**: {info['phenomena']}\n"
                    md += f"  - **等級**: {info['significance']}\n"
                    md += f"  - **時間**: {time_range['startTime']} ~ {time_range['endTime']}\n"

            st.markdown(md)

        # 顯示更新時間
        if self.last_alert_update:
            st.caption(f"📅 最後更新時間：{self.last_alert_update}")

    def start_scheduler(self):
        schedule.every(10).minutes.do(self.updateAlert)

    def make_space(self, space):
        st.markdown(f"<div style='height: {space}em'></div>", unsafe_allow_html=True)
