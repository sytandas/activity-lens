from models.ride import Ride

def main():
    ride = Ride("")
    ride.load_file()
    ride.fetch_weather()
    ride.calculate_metrics()
    ride.summary()

if __name__ == "__main__":
    main()
