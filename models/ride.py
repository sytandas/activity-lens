import os
import requests
import pandas as pd
import json
import fitdecode

API_KEY = os.getenv("")
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"

SEMICIRCLE = 180 / 2**31


class Ride:
    def __init__(self, fit_file):
        self.fit_file = fit_file
        self.record = []
        self.info = {}
        self.weather = None
        self.df = None
        self.metrics = {}

    def load_file(self):
        with fitdecode.FitReader(self.fit_file) as fit:
            for frame in fit:

                if isinstance(frame, fitdecode.FitDataMessage):

                    # Record messages
                    if frame.name == "record":
                        v = {
                            field.name: field.value
                            for field in frame.fields
                        }

                        lat = v.get("position_lat")
                        lon = v.get("position_long")

                        self.record.append({
                            "time": v.get("timestamp"),
                            "lat": lat * SEMICIRCLE if lat is not None else None,
                            "lon": lon * SEMICIRCLE if lon is not None else None,
                            "hr": v.get("heart_rate"),
                            "power": v.get("power"),
                            "distance_m": v.get("distance"),
                        })

                    # Session messages
                    elif frame.name == "session":
                        v = {
                            field.name: field.value
                            for field in frame.fields
                        }

                        self.info = {
                            "start": v.get("start_time"),
                            "duration_s": v.get("total_elapsed_time"),
                            "distance_m": v.get("total_distance"),
                        }

        self.df = pd.DataFrame(self.record)

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

        # Normalized Power approximation
        np_ = (
            (power.rolling(30).mean().dropna() ** 4).mean() ** 0.25
            if len(power) >= 30 else None
        )

        self.metrics = {
            "avg_power": power.mean() if not power.empty else None,
            "max_power": power.max() if not power.empty else None,
            "norm_power": np_,
            "avg_hr": hr.mean() if not hr.empty else None,
            "max_hr": hr.max() if not hr.empty else None,
        }

        return self.metrics

    def summary(self):
        m = self.metrics

        dist_km = (self.info.get("distance_m") or 0) / 1000
        mins = (self.info.get("duration_s") or 0) / 60

        print(f"Start:          {self.info.get('start')}")
        print(f"Distance:       {dist_km:.1f} km")
        print(f"Duration:       {mins:.0f} mins")

        if m["avg_power"] is not None:
            np_text = (
                f"{m['norm_power']:.0f} W"
                if m["norm_power"] is not None else "N/A"
            )
            print(f"Avg power:      {m['avg_power']:.0f} W (NP {np_text})")
        else:
            print("No power data")

        if m["avg_hr"] is not None:
            print(f"Avg HR:         {m['avg_hr']:.0f} bpm")
        else:
            print("No HR data")

        if self.weather:
            w = self.weather
            print(
                f"Weather:        {w['main']['temp']}°C, "
                f"{w['weather'][0]['description']}, "
                f"wind {w['wind']['speed']} m/s"
            )


if __name__ == "__main__":
    ride = Ride("/home/r/dev/activity-lens/models/test.fit")

    ride.load_file()
    ride.fetch_weather()
    ride.calculate_metrics()
    ride.summary()