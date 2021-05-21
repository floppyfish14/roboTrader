# roboTrader
This is a pet project setup to see whether an automated crypto robot will outcompete myself investing in bitcoin. Here are the main points:
- 1. Poll coinbase pro api every minute for current price of bitcoin
- 2. Add price to an array of 60 data points (1 per every min for an hour
- 3. Do a quick moving sum average (MSA) using pandas (faster than numpy)
- 4. If current price is above MSA sell, if below, buy
- 5. Trade no more than 2% of total Bitcoin or USD
- 6. Chart total Portfolio Value

## To setup
Create an account at coinbase pro. Create api keys, pass, and secret. Put these in the files specified in code in the '/keys' directory. For example, if you are using the sandbox api (for testing) it would be:
- /keys/sandbox-api.key
- /keys/sandbox-api.pass
- /keys/sandbox-api.secret

## To run
```
$ python3 main.py
00:59	 Adding 40941.36 to Moving Average array.
```
Your output should be similar to this. Enjoy!

After the time specified in main.py, the computer will make a decision whether to buy or sell. This decision will be displayed for you to see along with the current MSA and a portfolio value chart.
