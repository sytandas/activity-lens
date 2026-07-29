'''
    Report file take a fit file and paticular day effort - weather from open-meteo 
'''
import fitparse

# Load the FIT file
fitfile1 = fitparse.FitFile("coros-28.fit")
fitfile2 = fitparse.FitFile("strava-28.fit")


# Iterate over all messages of type "record"
# (other types include "device_info", "file_creator", "event", etc)
for record in fitfile1.get_messages("record"):

    # Records can contain multiple pieces of data (ex: timestamp, latitude, longitude, etc)
    for data in record:

        # Print the name and value of the data (and the units if it has any)
        if data.units:
            print(" * {}: {} ({})".format(data.name, data.value, data.units))
        else:
            print(" * {}: {}".format(data.name, data.value))

    print("---")