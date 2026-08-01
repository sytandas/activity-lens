from datetime import datetime
import requests
import json

#openWeatherMap API key
API_KEY = "bd31a44eced5cd8db6bccec47d8bc01a"

#city
city = "Panskura"

# API endpoint 
url = "https://api.openweathermap.org/data/2.5/weather"

# for particular day API endpoint 
url_dt = "https://api.openweathermap.org/data/3.0/onecall/timemachine"

params = {
    "q": city,
    "appid": API_KEY,
    "units": "metric"
}

response = requests.get(url, params=params)
response.raise_for_status()

data = response.json()

# saving the jshon for avoiding request overload
# Save JSON to a file
with open("weather1.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4)
print("Weather data saved to weather.json")

print("Current weather:")
print(f"City         : {data['name']}, {data['sys']['country']}")
print(f"Weather      : {data['weather'][0]['main']}")
print(f"Description  : {data['weather'][0]['description']}")
print(f"Temperature  : {data['main']['temp']} °C")
print(f"Feels Like   : {data['main']['feels_like']} °C")
print(f"Humidity     : {data['main']['humidity']} %")
print(f"Pressure     : {data['main']['pressure']} hPa")
print(f"Wind Speed   : {data['wind']['speed']} m/s")
print(f"Cloud Cover  : {data['clouds']['all']} %")
print(f"Visibility   : {data['visibility'] / 1000:.1f} km")

if "rain" in data:
    print(f"Rain (1 hr)  : {data['rain'].get('1h', 0)} mm")

def dewpt():
    temprature = float(data['main']['temp'])
    humidity = float(data['main']['humidity'])

    a = 17.27
    b = 237.7

    alpha = ((a * temprature) / (b + temprature)) + math.log(humidity / 100)
    dewpt = (b * alpha) / (a - alpha)