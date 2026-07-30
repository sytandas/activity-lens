'''
FIT file
   │
   ▼
parse binary
   │
   ▼
create Ride object
   │
   ▼
return Ride
'''
import fitdecode

SEMICIRCLE_TO_DEGREE = 180 / (2**31)

with fitdecode.FitReader('data/activities/coros-28.fit') as fit:
    for frame in fit:
        if isinstance(frame, fitdecode.FitDataMessage):
            if frame.name == 'record':
                # Grab whichever fields are present in this record
                timestamp = frame.get_value('timestamp', fallback=None)
                lat_raw = frame.get_value('position_lat', fallback=None)
                lon_raw = frame.get_value('position_long', fallback=None)
                altitude = frame.get_value('altitude', fallback=None)
                heart_rate = frame.get_value('heart_rate', fallback=None)
                speed = frame.get_value('speed', fallback=None)
                cadence = frame.get_value('cadence', fallback=None)

                lat = lat_raw * SEMICIRCLE_TO_DEGREE if lat_raw is not None else None
                lon = lon_raw * SEMICIRCLE_TO_DEGREE if lon_raw is not None else None

                print(timestamp, lat, lon, altitude, heart_rate, speed, cadence)