import folium
import pandas as pd

from lib.weatherHelper import *

class WeatherDataManager:
    def __init__(self, api_key):
        self.api_key = api_key
        self.weather_data = {"Station": None, "Now": None}
        
    def updateWeatherData(self, data_type):
        if data_type not in ["Station", "Now"]:
            return
    
        data = pd.read_json(WHEATHER_URL[data_type].format(key=self.api_key))
        self.weather_data[data_type] = pd.DataFrame(data["records"]["Station"])

        return self.weather_data[data_type]
    
    def getMap(self, data_type, only_wind=False, update=False, save=False):
        if data_type not in ["Station", "Now"]:
            return None

        if self.weather_data[data_type] is None or update:
            self.updateWeatherData(data_type)

        df = self.weather_data[data_type]
        center_lat = df["GeoInfo"].apply(lambda x: x["Coordinates"][1]["StationLatitude"]).mean()
        center_lon = df["GeoInfo"].apply(lambda x: x["Coordinates"][1]["StationLongitude"]).mean()
        
        m_map = folium.Map(location=[center_lat, center_lon], zoom_start=8)

        def make_marker(m, station):
            geo_info = station["GeoInfo"]
            weather_info = station["WeatherElement"]

            station_name = station["StationName"]
            latitude = geo_info["Coordinates"][1]["StationLatitude"]
            longitude = geo_info["Coordinates"][1]["StationLongitude"]

            wind_speed = weather_info["WindSpeed"]
            wind_direction = weather_info["WindDirection"]
            weather = weather_info["Weather"]

            popup_data = POPUP_HTML.format( # 格式化的顯示資料
                time=station["ObsTime"]["DateTime"], 
                station_name=station_name,
                weather=weather,
                temperature=weather_info["AirTemperature"],
                humidity=weather_info["RelativeHumidity"],
                wind_speed=wind_speed,
                wind_direction=wind_direction,
                air_pressure=weather_info["AirPressure"]
            )

            icon_name, icon_color = get_weather_maker_data(weather)

            folium.Marker( # 建立標記點
                location=[latitude, longitude],
                popup=folium.Popup(popup_data, max_width=300),
                tooltip=f"{station_name}<br><點擊查看詳細資訊>",
                icon=folium.Icon(color=icon_color, icon=icon_name, prefix="fa")
            ).add_to(m)

        def draw_arrow(m, start, wind_dir, wind_speed):
            if wind_speed <= 0:
                return

            lenght = wind_speed * WIND_LINE_SCALE
            end = compute_arrow_end(start[0], start[1], wind_dir, lenght) # 計算箭頭尾端的座標
            left_wing, right_wing = compute_arrow_wings(end[0], end[1], wind_dir, lenght) # 計算箭頭左右兩側的座標

            folium.PolyLine([start, end], color="blue", weight=3, tooltip=f"風速: {wind_speed} m/s").add_to(m)
            folium.PolyLine([end, left_wing], color="blue", weight=3).add_to(m)
            folium.PolyLine([end, right_wing], color="blue", weight=3).add_to(m)

        for index, station in df.iterrows():
            geo_info = station["GeoInfo"]
            weather_info = station["WeatherElement"]
            latitude = geo_info["Coordinates"][1]["StationLatitude"]
            longitude = geo_info["Coordinates"][1]["StationLongitude"]

            if not only_wind:
                make_marker(m_map, station)
            
            draw_arrow(m_map, (latitude, longitude), weather_info["WindDirection"], weather_info["WindSpeed"])

        if save:
            m_map.save("./output/weather.html")

        return m_map