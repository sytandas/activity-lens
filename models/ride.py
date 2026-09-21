'''
Ride
 │
 ├── Activity Info
 │     ├── start
 │     ├── duration
 │     ├── distance
 │
 ├── TrackPoint
 │      ├── lat
 │      ├── lon
 │      ├── hr
 │      ├── power
 │      └── weather
 │
 └── Summary
        ├── avg power
        ├── avg HR
        └── effort
'''
import requests
import json
import math 

API_KEY = ""

city = "Kolkata" # city 

url = "https://api.openweathermap.org/data/2.5/weather" # endpoint

params = {
    "q": city,
    "appid": API_KEY,
    "units": "metric"
}

response

class Ride:
    def __init__(self, fit_file):
        self.fit_file = fit_file
        self.records = []

    def load_file(self):
        ...

    def fetch_weather(self):
        ...

    def calculate_metrics(self):
        ...

    def summary(self):
        ...