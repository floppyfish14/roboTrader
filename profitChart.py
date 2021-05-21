import plotext as plx
from varData import *

def create_chart():
    #clear terminal and plot before updating plot
    plx.clp()
    plx.clt()
    #set chart color and title and size
    #use plx.colors() to find one that works for your terminal
    plx.canvas_color("iron")
    plx.title("RoboTrader Calculations")
    #plot data with a legend for identification purposes
    #plx.scatter(dailyUSDArray, label = "USD PNL")
    #plx.scatter(dailyBTCArray, label = "BTC PNL")
    plx.plot(portfolioValue, label = "Portfolio Value USD")
    #show the chart
    plx.sleep(0.001)
    plx.show()
    return
