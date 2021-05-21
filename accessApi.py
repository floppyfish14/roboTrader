"""
ALL REST requests for coinbasepro api must contain the following headers:
    CB-ACCESS-KEY - The api key as a string
    CB-ACCESS-SIGN - The base64-encoded signature
    CB-ACCESS-TIMESTAMP - A timestamp for your request
    CB-ACCESS-PASSPHRASE - The passphrase for your api key

ALL request bodies should have content type application/json and be valid json
"""

# Requires python-requests. Install with pip:
#
#   pip install requests
#
# or, with easy-install:
#
#   easy_install requests


#need pandas for the movingAverageArray calculation
#supposedly it is faster than numpy
import pandas as pd

from varData import *

# Create custom authentication for Exchange

def getAccounts(url, authentication):
    # Get accounts
    r = requests.get(url + 'accounts', auth=authentication)
    r = r.json()
    print(json.dumps(r, indent=3))
    return r
    # [{"id": "a1b2c3d4", "balance":...

def buyOrder(url, authentication, amount=100):

    #get balance first to make sure we have enough funds.
    totalUSD = getBalance(url, authentication, "USD")

    if float(totalUSD) <= float(amount):
        coinbaseTransfer(url, authentication)
    else:
        pass

    #make sure my algorithm doesn't use too much money
    #if float(amount) > 300:
    #    amount = 300.00
    #Must meet limit of 10.00 size for USD for coinbase pro
    if float(amount) <= 9.99:
        print("Must have a value greater than 9.99! Upgrading your request to $10.00")
        amount = 10.00
    else:
        pass

    #round to the nearest 100th for coinbase's API
    amount = round(amount, 2)
# Place an order
    order = {
        "funds": amount,
        "side": "buy",
        "type": "market",
        "product_id": "BTC-USD"
        }
    #Need to jsonify the order for the api to read it properly
    order = json.dumps(order)
    #Send the request to the api
    r = requests.post(url + 'orders', data=order, auth=authentication)
    #print(r.status_code)
    #print(r.text)
    return r

def sellOrder(url, authentication, amount=100):
    #retrieve data about balances in accounts
    accounts = requests.get(url + 'accounts', auth=authentication)
    jsonData = json.loads(accounts.text)
    lengthData = len(jsonData)
    for i in range(lengthData):
        if jsonData[i]["currency"] == "USD":
            totalBalance = jsonData[i]["balance"]
        else:
            pass
    #print("USD Balance: {}".format(totalBalance))
    #print(json.dumps(jsonData,indent=3))

    #make sure we sell more than $0.00
    if float(amount) <= 0.00:
        return print("Must sell something for more than 0!")
    if float(amount) >= float(totalBalance):
        return print("Cannot sell more than what you own!")
    else:
        pass

    #round to the nearest 100th for coinbase's API
    amount = round(amount, 2)

# Place an order
    order = {
        "size": amount,
        "side": "sell",
        "type": "market",
        "product_id": "BTC-USD"
        }
    #Need to jsonify the order for the api to read it properly
    order = json.dumps(order)
    #Send the request to the api
    r = requests.post(url + 'orders', data=order, auth=authentication)
    #print(r.status_code)
    #print(r.text)
    return r

def getPaymentMethods(url, authentication):
    #get payment methods setup for coinbase pro on your account
    r = requests.get(url + 'payment-methods', auth=authentication)
    jsonData = json.loads(r.text)
    # return account-id, type, and name
    lengthData = len(jsonData)
    for i in range(lengthData):
        print("ID: {}".format(jsonData[i]["id"]))
        print("Name: {}".format(jsonData[i]["name"]))
        print("Type: {}".format(jsonData[i]["type"]))
        print()
    return jsonData

def depositPayment(url, authentication, accountType):
    #use getPaymentMethods() to identify ach_bank and deposit money from there
    accounts = getPaymentMethods(url, authentication)
    #need to iterate over our list returned from getPaymentMethods
    #so we use len to help us
    lengthData = len(accounts)
    #accessing a list of lists to find the correct account to deposit from
    for i in range(lengthData):
        if accounts[i]["type"] == str(accountType): 
            accountFrom = accounts[i]["id"]
            print("Found the account: {}".format(accountFrom))
        else:
            pass

    depositInfo = {
            "amount": "1.00",
            "currency": "BTC",
            "payment_method_id": str(accountFrom)
            }
    #Need to jsonify the order for the api to read it properly
    depositInfo = json.dumps(depositInfo)
    r = requests.post(url + 'deposits/payment-method', auth=authentication, data=depositInfo)
    #Let us know if the money was deposited
    if r.status_code == 200:
        print("Got {}, must mean that we deposited 1.00 USD.".format(r.status_code))
    else:
        #print some helpful error message
        print(r.status_code)
        print(r.content)
    return r

def coinbaseTransfer(url, authentication, amount=300):

    if float(amount) <= 0.00:
        return print("Must have an amount higher than 0!")
    #Transfer funds internally from coinbase to coinbase pro
    r = requests.get(url + 'coinbase-accounts', auth=authentication)
    jsonData = json.loads(r.text)
    lengthData = len(jsonData)
    for i in range(lengthData):
        if jsonData[i]["name"] == "USD Wallet":
            accountFrom = jsonData[i]["id"]
        else:
            pass
    print("Found Coinbase account! Transferring Funds.")
    depositInfo = {
            "amount": float(amount),
            "currency": "USD",
            "coinbase_account_id": accountFrom
            }
    #Need to jsonify the order for the api to read it properly
    depositInfo = json.dumps(depositInfo)
    pr = requests.post(url + 'deposits/coinbase-account', auth=authentication, data=depositInfo)
    print(pr.status_code)
    print(pr.content)
    return jsonData

def getCurrentPrice(url=api_url, product="btc-usd"):
    r = requests.get(url + 'products/'+product+'/ticker')
    jsonData = json.loads(r.text)
    price = jsonData["price"]

    return float(price)

def gatherMovingAverage(url, product="btc-usd"):
    #Determine the moving average of BTC over the past hour
    #We want to make one transaction for every hour of the day
    #Let's take the moving average of the past 1 hours and see what happens
    global movingAverageArray

    r = requests.get(url + 'products/'+product+'/ticker')
    jsonData = json.loads(r.text)
    price = jsonData["price"]
    #print("Current price of {0}: {1}".format(product,price))
    print("\t Adding {} to Moving Average array.".format(price), end="\r")
    movingAverageArray.append(float(price))

    return price

def gatherPNL(url, authentication):
    global dailyUSDArray
    global dailyBTCArray
    #gather numbers to determine if we profited or lost today
    #based on 24 values (1 per hour)
    r = requests.get(url + 'accounts/', auth=authentication)
    jsonData = json.loads(r.text)
    lengthData = len(jsonData)
    for i in range(lengthData):
        if jsonData[i]["currency"] == "USD":
            accountUSD = jsonData[i]["id"]
        if jsonData[i]["currency"] == "BTC":
            accountBTC = jsonData[i]["id"]
        else:
            pass
    rUSD = requests.get(url +'accounts/' + accountUSD, auth=authentication)
    rBTC = requests.get(url +'accounts/' + accountBTC, auth=authentication)
    jsonUSD = json.loads(rUSD.text)
    jsonBTC = json.loads(rBTC.text)
    balanceUSD = jsonUSD["balance"]
    balanceBTC = jsonBTC["balance"]
    dailyUSDArray.append(float(balanceUSD))
    dailyBTCArray.append(float(balanceBTC))
    return

def calculatePNL(currency="USD"):
    if currency == "USD":
        global dailyUSDArray
        startPNL = dailyUSDArray[0]
        lastPNL = dailyUSDArray[-1]

    if currency == "BTC":
        global dailyBTCArray
        startPNL = dailyBTCArray[0]
        lastPNL = dailyBTCArray[-1]

    PNL = lastPNL - startPNL
    if PNL > 0:
        print("{:>75} -- Positive Profit: {}".format(currency,PNL))
    elif PNL == 0:
        print("{:>75} -- No Profit or Loss. PNL: {}".format(currency,PNL))
    else:
        print("{:>75} -- Negative Profit: {}".format(currency,PNL))
    return

def calculateMovingAverage(movingAverageArray=movingAverageArray,n=60):
    #number of series to calculate the moving average for
    movingAverage = pd.Series(movingAverageArray).rolling(window=n).mean().iloc[n-1:].values
    print("Calculated the moving average: {}".format(movingAverage),end="\r\n")
    determineOrder(float(movingAverage),"USD","BTC")
    return float(movingAverage)

def getBalance(url, authentication, currency="USD"):
    #retrieve data about balances in accounts
    accounts = requests.get(url + 'accounts', auth=authentication)
    jsonData = json.loads(accounts.text)
    lengthData = len(jsonData)
    for i in range(lengthData):
        if jsonData[i]["currency"] == currency:
            totalBalance = jsonData[i]["balance"]
        else:
            pass
    #print("Total balance of {0} is: {1}.".format(currency,totalBalance))
    return float(totalBalance)

def countdown(t=60):
    #make a cool countdown to display on the command line
    while t:
        mins, secs = divmod(t,60)
        timer = '{:02d}:{:02d}'.format(mins,secs)
        print(timer, end="\r")
        time.sleep(1)
        t -= 1
    return

def determineOrder(movingAverage, currency="USD", coin="BTC"):
    #call getBalance so you can figure out how much to trade for
    totalFiat = getBalance(api_url, auth, currency)
    totalCoin = getBalance(api_url, auth, coin)
    #get two percent of your totals
    buyingAmount = float(totalFiat) * 0.02
    sellingAmount = float(totalCoin) * 0.02

    #get current price of currency
    currentPrice = getCurrentPrice()
    if float(movingAverage) >= float(getCurrentPrice()):
        print("Buying {} with 2% of total Fiat. Buying Amount in USD: {}".format(coin,buyingAmount), end="\r")
        buyOrder(api_url, auth, float(buyingAmount))
    if float(movingAverage) <= float(currentPrice):
        print("Selling 2% of total {}. Selling Amount in {}: {}".format(coin,coin,sellingAmount),end="\r")
        sellOrder(api_url, auth, float(sellingAmount))
    return

#getAccounts(api_url, auth)
#buyOrder(api_url, auth, 300)
#sellOrder(api_url, auth, 300)
#getPaymentMethods(api_url, auth)
#depositPayment(api_url, auth, "ach_bank_account")
#coinbaseTransfer(api_url, auth)
#calcMovingAverage(api_url)
#getBalance(api_url, auth)
