'''
ride
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

response = requests.get(url, params=params)
response.raise_for_status()
data = response.json()

with open("weather1.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4)
print("weather data saved!")

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
'''

# test
"""
Ride
 ├── Activity Info: start, duration, distance
 ├── TrackPoint:    lat, lon, hr, power, weather
 └── Summary:       avg power, avg HR, effort

Requires: pip install fitparse requests
Set your key first:  export OPENWEATHER_API_KEY="..."
"""
import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional

import requests
from fitparse import FitFile

WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
SEMICIRCLE_TO_DEG = 180 / 2**31  # FIT stores lat/lon as semicircles

@dataclass
class TrackPoint:
    time: Optional[datetime] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    hr: Optional[int] = None
    power: Optional[int] = None
    weather: Optional[dict] = None


@dataclass
class Summary:
    avg_power: Optional[float] = None
    avg_hr: Optional[float] = None
    normalized_power: Optional[float] = None
    effort: Optional[float] = None  # TSS-style score (needs FTP)


class Ride:
    def __init__(self, fit_file, ftp=200, api_key=None):
        self.fit_file = fit_file
        self.ftp = ftp  # functional threshold power, used for effort
        self.api_key = api_key or os.environ.get("OPENWEATHER_API_KEY", "")
        self.records: list[TrackPoint] = []
        self.start = None
        self.duration = None   # seconds
        self.distance = None   # metres
        self.weather = None
        self._summary = Summary()

    # ---------- load ----------
    def load_file(self):
        fit = FitFile(self.fit_file)

        for msg in fit.get_messages("record"):
            v = msg.get_values()
            lat, lon = v.get("position_lat"), v.get("position_long")
            self.records.append(TrackPoint(
                time=v.get("timestamp"),
                lat=lat * SEMICIRCLE_TO_DEG if lat is not None else None,
                lon=lon * SEMICIRCLE_TO_DEG if lon is not None else None,
                hr=v.get("heart_rate"),
                power=v.get("power"),
            ))

        for msg in fit.get_messages("session"):
            v = msg.get_values()
            self.start = v.get("start_time")
            self.duration = v.get("total_elapsed_time")
            self.distance = v.get("total_distance")
            break

        if self.start is None and self.records:
            self.start = self.records[0].time
        return self

    # ---------- weather ----------
    def fetch_weather(self, save_to=None):
        """One call at the ride's first GPS fix, applied to every point."""
        first = next((r for r in self.records if r.lat is not None), None)
        if first is None:
            raise ValueError("No GPS points in this file.")

        params = {"lat": first.lat, "lon": first.lon,
                  "appid": self.api_key, "units": "metric"}
        resp = requests.get(WEATHER_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        self.weather = {
            "temp_c": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
            "wind_deg": data["wind"].get("deg"),
            "conditions": data["weather"][0]["description"],
        }
        for r in self.records:
            r.weather = self.weather

        if save_to:
            with open(save_to, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        return self.weather

    # ---------- metrics ----------
    def calculate_metrics(self):
        powers = [r.power for r in self.records if r.power is not None]
        hrs = [r.hr for r in self.records if r.hr is not None]

        s = self._summary
        s.avg_power = sum(powers) / len(powers) if powers else None
        s.avg_hr = sum(hrs) / len(hrs) if hrs else None

        # Normalized power: 30 s rolling mean -> ^4 -> mean -> ^0.25
        # (assumes ~1 Hz recording)
        if len(powers) >= 30:
            window = 30
            rolling = [sum(powers[i:i + window]) / window
                       for i in range(len(powers) - window + 1)]
            s.normalized_power = (sum(p ** 4 for p in rolling) / len(rolling)) ** 0.25

            # Effort as TSS = (sec * NP * IF) / (FTP * 3600) * 100
            secs = self.duration or len(powers)
            intensity = s.normalized_power / self.ftp
            s.effort = (secs * s.normalized_power * intensity) / (self.ftp * 3600) * 100
        return s

    # ---------- summary ----------
    def summary(self):
        if self._summary.avg_power is None and self._summary.avg_hr is None:
            self.calculate_metrics()
        s = self._summary
        return {
            "activity": {
                "start": self.start.isoformat() if self.start else None,
                "duration_min": round(self.duration / 60, 1) if self.duration else None,
                "distance_km": round(self.distance / 1000, 2) if self.distance else None,
            },
            "weather": self.weather,
            "summary": {k: (round(v, 1) if v is not None else None)
                        for k, v in asdict(s).items()},
        }

if __name__ == "__main__":
    ride = Ride("ride.fit", ftp=220).load_file()
    ride.fetch_weather(save_to="weather1.json")
    print(json.dumps(ride.summary(), indent=2))