from requests.auth import AuthBase
import json, hmac, hashlib, time, requests, base64, array, os

#get PWD for file purposes
pwd = os.getcwd()

#specify that it is binary data so nothing gets lost in translation
API_KEY = open(pwd+'/keys/sandbox-api.key','r',encoding="utf-8").read().rstrip('\n')
API_SECRET = open(pwd+'/keys/sandbox-api.secret','r',encoding="utf-8").read().rstrip('\n')
API_PASS = open(pwd+'/keys/sandbox-api.pass','r',encoding="utf-8").read().rstrip('\n')


#create the movingAverage array
#our bot uses this for it's calculations
#on whether to buy or sell every hour
movingAverageArray = array.array('f', [])
#create a daily profit and loss array to calculate if you are winning or losing
#it is a float array to calculate down to the small decimals
dailyUSDArray = array.array('f', [])
dailyBTCArray = array.array('f', [])

#create a portfolio balnce array for graphing
portfolioValue = array.array('f', [])

#keep a tally of buys and sells per hour
#gonna use this as a stop limit
buysPerHour = 0
sellsPerHour = 0

class CoinbaseExchangeAuth(AuthBase):
    def __init__(self, api_key, secret_key, passphrase):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase

    def __call__(self, request):
        timestamp = str(time.time())
        message = timestamp + request.method + request.path_url + (request.body or '')
        message = message.encode('utf-8')
        hmac_key = base64.b64decode(self.secret_key)
        signature = hmac.new(hmac_key, message, hashlib.sha256)
        signature_b64 = base64.b64encode(signature.digest()).decode('utf-8')

        request.headers.update({
            'CB-ACCESS-SIGN': signature_b64,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        })
        return request

#Use only after testing is complete!
#api_url='https://api.pro.coinbase.com/'
api_url = "https://api-public.sandbox.pro.coinbase.com/"
auth = CoinbaseExchangeAuth(API_KEY, API_SECRET, API_PASS)
