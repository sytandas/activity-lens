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

class Ride:
    def __init__(self, fit_file):
        self.fit_file = fit_file
        self.records = []

    def load(self):
        ...

    def fetch_weather(self):
        ...

    def calculate_metrics(self):
        ...

    def summary(self):
        ...