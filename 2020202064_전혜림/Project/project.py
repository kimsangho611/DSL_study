import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

commission = 0.00015
tax = 0.0025


class Trade:
    def __init__(self, initial_funds):
        self.initial_funds = initial_funds
        self.least_funds = initial_funds * 0.2
        self.investable_funds = initial_funds * 0.8
        self.stock_amount = 0

    def BuyStock(self, stock_price):
        amount_buy = self.investable_funds // stock_price
        if amount_buy <= 0:
            return False
        commission_buy = stock_price * amount_buy * commission
        if self.investable_funds - stock_price * amount_buy - commission_buy < 0:
            while True:
                amount_buy -= 1
                commission_buy = stock_price * amount_buy * commission
                if self.investable_funds - stock_price * amount_buy - commission_buy > 0:
                    break

        self.stock_amount += amount_buy
        self.investable_funds -= stock_price * amount_buy + commission_buy
        self.initial_funds = self.investable_funds + self.least_funds
        return True

    def SellStock(self, stock_price):
        if self.stock_amount <= 0:
            return False

        commission_sell = (stock_price * self.stock_amount) * (commission + tax)
        self.investable_funds += self.stock_amount * stock_price
        self.investable_funds -= commission_sell
        self.stock_amount = 0
        self.initial_funds = self.investable_funds + self.least_funds
        return True

def SetInitial():
    data = pd.read_csv("./data/삼성전자_일봉.csv", header=None,
                       names=['종목명', '종목코드', '날짜', '시가', '고가', '저가', '종가', '거래량'], encoding="CP949")
    data = data.sort_values(by=['날짜'])
    data = data.reset_index(drop=True)

    trading_vol = 0
    for k in range(len(data.index)):
        trading_vol += data['거래량'].iloc[k]
    trading_vol /= len(data.index)

    data['ema12'] = data['종가'].ewm(span=12).mean()
    data['ema26'] = data['종가'].ewm(span=26).mean()
    data['MACD'] = data.apply(lambda x: (x["ema12"] - x["ema26"]), axis=1)
    data['MACD_signal'] = data['MACD'].ewm(span=9).mean()
    data["MACD_oscillator"] = data.apply(lambda x: (x["MACD"] - x["MACD_signal"]), axis=1)
    data["MACD_sign"] = data.apply(lambda x: ("매수" if (0 > x["MACD"] > x["MACD_signal"])
                                              else ("매도" if 0 < x["MACD"] < x["MACD_signal"] else 0)), axis=1)
    data["MACD_sign_with_volume"] = data.apply(lambda x: (
        "매수" if (0 > x["MACD"] > x["MACD_signal"] and x['거래량'] >= trading_vol)
        else ("매도" if 0 < x["MACD"] < x["MACD_signal"] and x['거래량'] >= trading_vol else 0)), axis=1)
    return data

"""
plt.rc('font', family='Malgun Gothic')
plt.rcParams['axes.unicode_minus'] = False

xtick = []
for i in np.arange(0, 64, 8):
    xtick.append(str(stock_data['날짜'].iloc[i]))

# MACD, MACD signal chart
plt.subplot(2, 1, 1)
plt.title("MACD chart")
plt.plot(stock_data.index, stock_data["MACD"], stock_data["MACD_signal"])
for i in range(len(stock_data.index)):
    if stock_data["MACD_sign"].iloc[i] == "매수":
        plt.scatter(stock_data.index[i], stock_data["MACD"].iloc[i], color="r")
    elif stock_data["MACD_sign"].iloc[i] == "매도":
        plt.scatter(stock_data.index[i], stock_data["MACD"].iloc[i], color="b")
plt.axhline(y=0, color='r', linewidth=1)
plt.xticks(fontsize=6, rotation=45)
plt.xticks(np.arange(0, 64, 8), xtick)

# Oscillator bar
plt.subplot(2, 1, 2)
plt.title("MACD oscillator")
oscillator = stock_data["MACD_oscillator"]
plt.bar(list(stock_data.index), list(oscillator.where(oscillator > 0)), 0.7)
plt.bar(list(stock_data.index), list(oscillator.where(oscillator < 0)), 0.7)
plt.axhline(y=0, color='r', linewidth=1)
plt.xticks(fontsize=6, rotation=45)
plt.xticks(np.arange(0, 64, 8), xtick)

plt.subplots_adjust(hspace=0.8)
plt.show()
"""


# backtesting
stock_data = SetInitial()
initial_money = int(input("initial money : "))
testing = Trade(initial_money)

sell_count = 0
buy_count = 0

for i in range(len(stock_data.index)):
    if stock_data['MACD_sign_with_volume'].iloc[i] == '매수' or stock_data['MACD_sign_with_volume'].iloc[i] == '매도':
        print("\033[0m", end="")
        if stock_data['MACD_sign_with_volume'].iloc[i] == '매수':
            if testing.BuyStock(stock_data['시가'].iloc[i]):
                print('\033[95m', end="")
                print(str(stock_data['MACD_sign_with_volume'].iloc[i]) + " " + str(stock_data['날짜'].iloc[i])
                      + " 시가 : " + str(stock_data['시가'].iloc[i]), end="")
                print("\n자금 : " + str(testing.initial_funds) + " 보유 주식 : " + str(testing.stock_amount) + '\n')
                buy_count += 1

        elif stock_data['MACD_sign_with_volume'].iloc[i] == '매도':
            if testing.SellStock(stock_data['시가'].iloc[i]):
                print('\033[96m', end="")
                print(str(stock_data['MACD_sign_with_volume'].iloc[i]) + " " + str(stock_data['날짜'].iloc[i])
                      + " 시가 : " + str(stock_data['시가'].iloc[i]), end="")
                print("\n자금 : " + str(testing.initial_funds) + " 보유 주식 : " + str(testing.stock_amount) + '\n')
                sell_count += 1

    elif i == len(stock_data.index) - 1:
        testing.SellStock(stock_data['시가'].iloc[i])
        sell_count += 1
        print("매도 " + str(stock_data['날짜'].iloc[i]) + " " + " 시가 : " + str(stock_data['시가'].iloc[i]))

print("\nsell_count : " + str(sell_count) + "\nbuy_count : " + str(buy_count))
print("before investment : " + str(initial_money))
print("after investment : " + str(testing.initial_funds))
