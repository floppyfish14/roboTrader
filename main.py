#import our vars
from varData import *

import accessApi as api
import profitChart as pC
import os, array

def main():
    #time in seconds to wait until next polling of price
    timeWait = 10

    #amount of datapoints to have in moving average array before
    #making a decision
    arrayCount = 60

    #need this to determine when to delete array
    dataPerMinute = 60/timeWait
    dataPerHour = dataPerMinute*60

    #begin aggregating our data for future smart decisions
    api.gatherMovingAverage(api_url)

    #display a countdown for fun
    api.countdown(int(timeWait))

    #if we have a proper array length (it is divisible by our arrayCount counter), calculate the moving average
    #basically, if we gathered as much data as we wanted to, then the movingAverageArray should be divisble by the array counter
    if (len(movingAverageArray)/int(arrayCount)).is_integer():
        api.calculateMovingAverage(movingAverageArray, len(movingAverageArray))

        api.getPortfolioBalance(api_url, auth)

        #create a live chart to display
        pC.create_chart()

    #if the moving average array is greater than 12hours old delete it
    #this is to avoid a perpetual cycle of buying or selling
    elif (len(movingAverageArray) > dataPerHour*12):
        del movingAverageArray[:]

    else:
        pass

while True:
    if __name__ == "__main__":
        main()
