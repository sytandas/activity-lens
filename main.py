from models.ride import Ride

def main():
    ride = Ride("data/activities/coros-28.fit")
    ride.load()
    ride.fetch_weather()
    ride.calculate_metrics()
    ride.summary()

if __name__ == "__main__":
    main()
