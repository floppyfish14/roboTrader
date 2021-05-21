#import our vars
from varData import *

import accessApi as api
import profitChart as pC
import os, array

def main():
    #time in seconds to wait until next polling of price
    timeWait = 10

    #amount of numbers to have in moving average array before
    #making a decision
    arrayCount = 6

    #start off with getting current balances
    #api.gatherPNL(api_url, auth)
    #api.gatherPNL(api_url, auth)

    #begin aggregating our data for future smart decisions
    api.gatherMovingAverage(api_url)

    #display a 60 second countdown for fun
    api.countdown(int(timeWait))

    #if length of array is = 60, calculate the moving average
    if (len(movingAverageArray)/int(arrayCount)).is_integer():
        api.calculateMovingAverage(movingAverageArray, len(movingAverageArray))

        #gather new PNL values for calculations
        #api.gatherPNL(api_url, auth)
        #api.gatherPNL(api_url, auth)

        #calculate whether we are profiting or losing
        #still haven't figured out how to track loss
        #due to trading from USD to BTC or vice versa
        #api.calculatePNL("BTC")
        #api.calculatePNL("USD")
        api.getPortfolioBalance(api_url, auth)

        #create a live chart to display
        pC.create_chart()

    else:
        pass

while True:
    if __name__ == "__main__":
        main()
