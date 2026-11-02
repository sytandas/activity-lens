import os
import requests
import pandas as pd
import json
from fitparse import FitFile
from dotenv import load_dotenv
import fitdecode

load_dotenv()
API_KEY = os.getenv("<key>")
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather" # endpoint
SEMICIRCLE = 180/2**31 # for fit generally save fit file in semi cricle 

class Ride:
    def __init__(self, fit_file):
        self.fit_file = fit_file
        self.record = []
        self.info = {}
        self.weather = None
        self.df = None

    def load_file(self):
        fit = FitFile(self.fit_file)

        for msg in fit.get_messages("record"):
            v = msg.get_values()
            lat, lon = v.get("position_lat"), v.get("position_long")
            self.record.append({
                "time": v.get("timestamp"),
                "lat": lat * SEMICIRCLE if lat is not None else None,
                "lon": lon * SEMICIRCLE if lon is not None else None,
                "hr": v.get("heart_rate"),
                "power": v.get("power"),
                "distance_m": v.get("distance"), 
            })

        self.df = pd.DataFrame(self.record)

        for msg in fit.get_messages("session"):
            v = msg.get_values()
            self.info = {
                "start": v.get("start_time"),
                "duration_s": v.get("total_elapsed_time"),
                "distance_m": v.get("total_distance"),
            }
            break

    def fetch_weather(self, save_path="weather.json"):
        # using the actual start location
        pts = self.df.dropna(subset=["lat", "lon"])
        if pts.empty:
            raise ValueError("no gps data found")
        first = pts.iloc[0]

        r = requests.get(WEATHER_URL, params={
            "lat": first['lat'], 
            "lon": first['lon'],
            "appid": "c5b7c09cdb5b5c330309c4a6c225971e",
            "units": "metrics",
        }, timeout=10)
        r.raise_for_status()
        self.weather = r.json()

        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(self.weather, f, indent=4)
        print("weather data saved")

    def calculate_metrics(self):
        power = self.df["power"].dropna()
        hr = self.df["hr"].dropna()
        # Normalized power: 30s rolling avg -> ^4 -> mean -> ^0.25
        # (assumes ~1 Hz recording)
        np_ = (power.rolling(30).mean().dropna() ** 4).mean() ** 0.25 if len(power) >= 30 else None

        self.metrics = {
            "avg_power": power.mean() if not power.empty else None,
            "max_power": power.max() if not power.empty else None,
            "norm_power": np_,
            "avg_hr": hr.mean() if not hr.empty else None,
            "max_hr": hr.max() if not hr.empty else None,
        }
        return self.metrics


    def summery(self):
        m = self.metrics
        dist_km = (self.info.get("distance_m" or 0)) / 1000
        mins = (self.info.get("duration_s" or 0)) / 60

        print(f"Start:          {self.info.get('start')}")
        print(f"Distance:       {dist_km: .1f} km")
        print(f"Duration:       {mins: .0f} mins")
        print(f"Avg power:      {m['avg_power']:.0f} W  (NP {m['norm_power']:.0f} W)" if m["avg_power"] else "No power data")
        print(f"Avg HR:         {m['avg_hr']:.0f} bpm" if m["avg_hr"] else "No HR data")
        if self.weather:
            w = self.weather
            print(f"Weather:    {w['main']['temp']}°C, {w['weather'][0]['description']}, wind {w['wind']['speed']} m/s")


if __name__ == "__main__":
    ride = Ride("te1.fit")
    ride.load_file()
    ride.fetch_weather()
    ride.calculate_metrics()
    ride.summery()