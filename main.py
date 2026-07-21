import math

temperature = float(input("Enter temperature (°C): "))
humidity = float(input("Enter relative humidity (%): "))

a = 17.27
b = 237.7

# Magnus-Tetens Formula
alpha = ((a * temperature) / (b + temperature)) + math.log(humidity / 100.0)
dew_point = (b * alpha) / (a - alpha)

print(f"Dew Point: {dew_point:.2f} °C")

if dew_point < 10:
    print("Very dry, good for racing")
elif 10 <= dew_point < 13:
    print("Comfortable, minimal impact")
elif 13 <= dew_point < 16:
    print("Slightly humid, small increase of effort")
elif 16 <= dew_point < 18:
    print("Noticeable, pace may slow slightly")
elif 18 <= dew_point < 21:
    print("Uncomfortable, noticeable performance loss")
elif 21 <= dew_point < 24:
    print("Very humid, significant slowdown")
else:  # dew_point >= 24
    print("Oppressive, high heat stress risk")