import win32com.client
import time
import os
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import matplotlib.pylab as plt

commission = 0.00015
tax = 0.0025


class trade:
    def __init__(self, initial_funds):
        self.initial_funds = initial_funds
        self.least_funds = initial_funds * 0.2
        self.investable_funds = initial_funds * 0.8
        self.stock_amount = 0

    def BuyStock(self, stock_price):
        amount_buy = self.investable_funds // stock_price
        if amount_buy <= 0:
            return
        commission_buy = stock_price * amount_buy * commission
        print(commission_buy)
        if self.investable_funds - stock_price * amount_buy - commission_buy < 0:
            while True:
                amount_buy -= 1
                commission_buy = stock_price * amount_buy * commission
                if self.investable_funds - stock_price * amount_buy - commission_buy > 0:
                    break
        self.stock_amount += amount_buy
        self.investable_funds -= stock_price * amount_buy + commission_buy
        self.initial_funds = self.investable_funds + self.least_funds

    def SellStock(self, stock_price):
        if self.stock_amount <= 0:
            return
        commission_sell = (stock_price * self.stock_amount) * commission + (stock_price * self.stock_amount) * tax
        print(commission_sell)
        self.investable_funds += self.stock_amount * stock_price
        self.investable_funds -= commission_sell
        self.stock_amount = 0
        self.initial_funds = self.investable_funds + self.least_funds


stock_data = pd.read_csv("./data/삼성전자_1분봉.csv", header=None,
                         names=['종목명', '종목코드', '날짜', '시간', '시가', '고가', '저가', '종가', '거래량'], encoding="CP949")

stock_data = stock_data.sort_values(by=['날짜', '시간'])
stock_data = stock_data.reset_index(drop=True)

trading_vol = 0
for i in range(len(stock_data.index)):
    trading_vol += stock_data['거래량'].iloc[i]
trading_vol /= len(stock_data.index)

stock_data['ema12'] = stock_data['종가'].ewm(span=12).mean()
stock_data['ema26'] = stock_data['종가'].ewm(span=26).mean()
stock_data['macd'] = stock_data.apply(lambda x: (x["ema12"] - x["ema26"]), axis=1)
stock_data['macd_signal'] = stock_data['macd'].ewm(span=9).mean()
stock_data["macd_sign"] = stock_data.apply(
    lambda x: ("매수" if (0 > x["macd"] > x["macd_signal"]) else ("매도" if 0 < x["macd"] < x["macd_signal"] else 0)),
    axis=1)
stock_data["macd_sign_with_volume"] = stock_data.apply(lambda x: (
    "매수" if (0 > x["macd"] > x["macd_signal"] and x['거래량'] >= trading_vol) else (
        "매도" if 0 < x["macd"] < x["macd_signal"] and x['거래량'] >= trading_vol else 0)), axis=1)

plt.rc('font', family='Malgun Gothic')
plt.rcParams['axes.unicode_minus'] = False

xtick = []
for i in np.arange(0, 8000, 1000):
    xtick.append(str(stock_data['날짜'].iloc[i]) + " " + str(stock_data['시간'].iloc[i]))

"""
plt.plot( stock_data.index, stock_data['거래량'], label='거래량')
plt.axhline(y=trading_vol, color='r', linewidth=1)
plt.xticks(rotation=45)
plt.legend()
plt.xticks(np.arange(0, 8000, 1000), xtick)
plt.show()

plt.plot(stock_data.index, stock_data['macd'], label='macd')
plt.plot( stock_data.index, stock_data['macd_signal'], label='macd_signal')
plt.axhline(y=0, color='r', linewidth=1)
plt.xticks(rotation=45)
plt.legend()
plt.xticks(np.arange(0, 8000, 1000), xtick)
plt.show()
"""

testing = trade(10000000)

sell_count = 0
buy_count = 0
for i in range(len(stock_data.index)):
    if stock_data['macd_sign_with_volume'].iloc[i] == '매수' or stock_data['macd_sign_with_volume'].iloc[i] == '매도':
        print("\033[0m")

        if stock_data['macd_sign_with_volume'].iloc[i] == '매수':
            print('\033[95m')
            print("\n자금 : " + str(testing.initial_funds) + " 보유 주식 : " + str(testing.stock_amount))
            testing.BuyStock(stock_data['시가'].iloc[i])
            buy_count += 1
        elif stock_data['macd_sign_with_volume'].iloc[i] == '매도':
            print('\033[96m')
            print("\n자금 : " + str(testing.initial_funds) + " 보유 주식 : " + str(testing.stock_amount))
            testing.SellStock(stock_data['시가'].iloc[i])
            sell_count += 1
        print(str(stock_data['macd_sign_with_volume'].iloc[i]) + " " + str(stock_data['날짜'].iloc[i]) + " " + str(
            stock_data['시간'].iloc[i]) + " 시가 : " + str(stock_data['시가'].iloc[i]))
    elif i == len(stock_data.index) - 1:
        testing.SellStock(stock_data['시가'].iloc[i])
        sell_count += 1
        print(str(stock_data['macd_sign_with_volume'].iloc[i]) + " " + str(stock_data['날짜'].iloc[i]) + " " + str(
            stock_data['시간'].iloc[i]) + " 시가 : " + str(stock_data['시가'].iloc[i]))

print("\nsell_count : " + str(sell_count) + "\nbuy_count : " + str(buy_count))

print("before investment : 10000000")
print("after investment : " + str(testing.initial_funds))


# the profit before calculating tax and commission was about 800000 won in a month
# the profit after calculating tax and commission is now deficit
