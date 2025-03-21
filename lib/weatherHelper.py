import math

WHEATHER_URL = {
    "Station": "https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0001-001?Authorization={key}",
    "Now": "https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0003-001?Authorization={key}",
}


ALERT_URL = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/W-C0033-001?Authorization={key}"
FORECAST_URL = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization={key}"

WEATHER_DICT = {
    "晴": ["sun", "orange"],
    "陰": ["cloud", "gray"],
    "有雨": ["cloud-rain", "blue"],
    "多雲": ["cloud-sun", "cadetblue"],
    "多雲有雨": ["cloud-sun-rain", "blue"],
}

WEATHER_ICON_DICT = {
    "1": "☀️",
    "2": "🌤️",
    "3": "⛅",
    "4": "🌧️",
    "5": "🌩️"
}

POPUP_HTML = """
    <b>資料時間：</b> {time} <br>
    <b>測站名稱：</b> {station_name} <br>
    <b>天氣狀況：</b> {weather} <br>
    <b>氣溫：</b> {temperature}°C <br>
    <b>相對濕度：</b> {humidity}% <br>
    <b>風速：</b> {wind_speed} m/s <br>
    <b>風向：</b> {wind_direction}° <br>
    <b>氣壓：</b> {air_pressure} hPa
"""

WIND_LINE_SCALE = 0.03

def get_weather_icon(weather_code):
    return WEATHER_ICON_DICT.get(weather_code, "❓")

def get_weather_maker_data(weather):
    return WEATHER_DICT.get(weather, ["question", "black"])

def compute_arrow_end(lat, lon, wind_dir, length):
    rad = math.radians(float(wind_dir))
    end_lat = lat + length * math.cos(rad)
    end_lon = lon + length * math.sin(rad)
    return [float(end_lat), float(end_lon)]

def compute_arrow_wings(lat, lon, wind_dir, length, angle=25):
    rad_right = math.radians(float(wind_dir) + angle)
    rad_left = math.radians(float(wind_dir) - angle)

    wing_length = min(0.05, length * 0.1)
    left_lat = lat - wing_length * math.cos(rad_left)
    left_lon = lon - wing_length * math.sin(rad_left)
    right_lat = lat - wing_length * math.cos(rad_right)
    right_lon = lon - wing_length * math.sin(rad_right)

    return [left_lat, left_lon], [right_lat, right_lon]