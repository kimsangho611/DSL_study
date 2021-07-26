import win32com.client
import time
import os
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import matplotlib.pylab as plt

"""
class DataCollection:
    def __init__(self, stockName, startDay=19000101, endDay=20210101, StoreLocation=None):
        self.StockChart = win32com.client.Dispatch("CpSysDib.StockChart")
        self.CpStockCode = win32com.client.Dispatch("CpUtil.CpStockCode")

        self.stockName = stockName
        self.stockCode = self.CpStockCode.NameToCode(stockName)
        self.startDay = startDay
        self.endDay = endDay

        if not os.path.isdir(store_path):
            os.mkdir(store_path)
        self.StoreLocation = StoreLocation + '{}.csv'

    def CollectMinute(self, StockName, StockCode, timeperiod=5):
        s_day = datetime.strptime(str(self.startDay), '%Y%m%d')
        e_day = datetime.strptime(str(self.endDay), '%Y%m%d')
        date_list = [int((e_day - timedelta(days=i)).strftime("%Y%m%d")) for i in range((e_day - s_day).days + 1)]

        self.StockChart.SetInputValue(0, StockCode)
        self.StockChart.SetInputValue(1, ord('2'))  # 개수로 요청
        self.StockChart.SetInputValue(4, 2000)  # 몇개의 데이터를 수신할 지
        self.StockChart.SetInputValue(5, [0, 1, 2, 3, 4, 5, 8])  # 어떤 데이터를 받을 지
        self.StockChart.SetInputValue(6, ord('m'))  # 차트 종류
        self.StockChart.SetInputValue(7, timeperiod)  # 몇 분봉으로 받을지
        self.StockChart.SetInputValue(9, ord('1'))  # 수정주가 사용

        self.StockChart.BlockRequest()  # 데이터 요청
        time.sleep(0.3)

        receive = self.StockChart.GetHeaderValue(3)
        with open(self.StoreLocation.format(StockName + '_' + str(timeperiod) + '분봉'), 'w') as f:
            for i in range(receive):
                t = self.StockChart.GetDataValue(0, i)
                if (self.startDay <= t) and (t <= self.endDay):
                    f.write("{},{},{},{},{},{},{},{},{}\n".format(
                        StockName, StockCode,
                        self.StockChart.GetDataValue(0, i),
                        self.StockChart.GetDataValue(1, i),
                        self.StockChart.GetDataValue(2, i),
                        self.StockChart.GetDataValue(3, i),
                        self.StockChart.GetDataValue(4, i),
                        self.StockChart.GetDataValue(5, i),
                        self.StockChart.GetDataValue(6, i)
                    ))

            finish = False
            while self.StockChart.Continue:
                self.StockChart.BlockRequest()  # 데이터 요청
                time.sleep(0.3)
                receive = self.StockChart.GetHeaderValue(3)  # 총 수신 개수

                for i in range(receive):
                    t = self.StockChart.GetDataValue(0, i)
                    if (self.startDay <= t) and (t <= self.endDay):
                        f.write("{},{},{},{},{},{},{},{},{}\n".format(
                            StockName, StockCode,
                            self.StockChart.GetDataValue(0, i),
                            self.StockChart.GetDataValue(1, i),
                            self.StockChart.GetDataValue(2, i),
                            self.StockChart.GetDataValue(3, i),
                            self.StockChart.GetDataValue(4, i),
                            self.StockChart.GetDataValue(5, i),
                            self.StockChart.GetDataValue(6, i)
                        ))
                    elif t < self.endDay:
                        finish = True
                        break
                if finish:
                    break

    def CollectDay(self, StockName, StockCode):
        self.StockChart.SetInputValue(0, StockCode)
        self.StockChart.SetInputValue(1, ord('1'))  # 기간으로 요청
        self.StockChart.SetInputValue(2, self.endDay)  # 기간으로 요청
        self.StockChart.SetInputValue(3, self.startDay)  # 기간으로 요청
        self.StockChart.SetInputValue(5, [0, 2, 3, 4, 5, 8])  # 어떤 데이터를 받을 지
        self.StockChart.SetInputValue(6, ord('D'))  # 차트 종류
        self.StockChart.SetInputValue(9, ord('1'))  # 수정주가 사용

        self.StockChart.BlockRequest()
        time.sleep(0.3)

        receive = self.StockChart.GetHeaderValue(3)
        with open(self.StoreLocation.format(StockName + '_일봉'), 'w') as f:
            for i in range(receive):
                f.write("{},{},{},{},{},{},{},{}\n".format(
                    StockName, StockCode,
                    self.StockChart.GetDataValue(0, i),
                    self.StockChart.GetDataValue(1, i),
                    self.StockChart.GetDataValue(2, i),
                    self.StockChart.GetDataValue(3, i),
                    self.StockChart.GetDataValue(4, i),
                    self.StockChart.GetDataValue(5, i)
                ))

    def run(self, collect_type='일봉', period=None):
        if collect_type == '일봉':
            self.CollectDay(self.stockName, self.stockCode)
        elif collect_type == '분봉':
            if period == None:
                raise Exception("분봉을 수집하기 위해 기간을 설정해야합니다. (ex. 5분봉시 period = 5)")
            else:
                self.CollectMinute(self.stockName, self.stockCode, period)


if __name__ == '__main__':
        store_path  : 데이터를 저장하기 위한 디렉토리 path
        stockName   : 수집하기 위한 종목 이름
        ------------------------------------------------------
        DataCollection class 

        init function

        stockName       : 종목이름      (type: string, ex) '삼성전자')
        startDay        : 수집 시작 일자 (type: int, ex) 20200101) (조건 : startDay < endDay)
        endDay          : 수집 종료 일자 (type: int, ex) 20200201) (조건 : startDay < endDay)
        StoreLocation   : 데이터 저장 디렉토리 (ex) './data/')
        -------------------------------------------------------
        run function

        collect_type    : 수집하고자 하는 봉 종류(일봉, 분봉) (type: string, ex) '일봉')
        period          : collect_type이 분봉인 경우 사용하며 분봉 간격을 의미 (type: int, ex) 5분봉 -> period = 5)
        -------------------------------------------------------
        사용 예시

        store_path = './data/'
        stockName = "컴투스"
        d = DataCollection(stockName, 20210101, 20210201, store_path)
        d.run('분봉', 5)

store_path = './data/'
stockName = input("종목 : ")
d = DataCollection(stockName, 20210101, 20210201, store_path)
d.run('분봉', 1)
"""
stock_data = pd.read_csv("./data/삼성전자_1분봉.csv", header=None, names=['종목명', '종목코드', '날짜', '시간', '시가', '고가', '저가', '종가', '거래량'], encoding="CP949")

stock_data = stock_data.sort_values(by=['날짜', '시간'])
stock_data = stock_data.reset_index(drop=True)

trading_vol = 0
for i in range(len(stock_data.index)):
    trading_vol += stock_data['거래량'].iloc[i]
trading_vol /= len(stock_data.index)

stock_data['ema12'] = stock_data['종가'].ewm(span=12).mean()
stock_data['ema26'] = stock_data['종가'].ewm(span=26).mean()
stock_data['macd'] = stock_data.apply(lambda x: (x["ema12"]-x["ema26"]), axis=1)
stock_data['macd_signal'] = stock_data['macd'].ewm(span=9).mean()
stock_data["macd_sign"] = stock_data.apply(lambda x: ("매수" if (0 > x["macd"] > x["macd_signal"]) else ("매도" if 0 < x["macd"] < x["macd_signal"] else 0)), axis=1)
stock_data["macd_sign_with_volume"] = stock_data.apply(lambda x: ("매수" if (0 > x["macd"] > x["macd_signal"] and x['거래량'] >= trading_vol) else ("매도" if 0 < x["macd"] < x["macd_signal"] and x['거래량'] >= trading_vol else 0)), axis=1)


plt.rc('font', family='Malgun Gothic')
plt.rcParams['axes.unicode_minus'] = False

xtick = []
for i in np.arange(0, 8000, 1000):
    xtick.append(str(stock_data['날짜'].iloc[i]) + " " + str(stock_data['시간'].iloc[i]))

plt.plot(stock_data.index, stock_data['시가'])
plt.xticks(rotation=45)
plt.xticks(np.arange(0, 8000, 1000), xtick)
plt.show()

plt.plot(stock_data.index, stock_data['macd'], stock_data['macd_signal'])
plt.axhline(y=0, color='r', linewidth=1)
plt.xticks(rotation=45)
plt.xticks(np.arange(0, 8000, 1000), xtick)
plt.show()

sell_count = 0
buy_count = 0
for i in range(len(stock_data.index)):
    if stock_data['macd_sign_with_volume'].iloc[i] == '매수' or stock_data['macd_sign_with_volume'].iloc[i] == '매도':
        if stock_data['macd_sign_with_volume'].iloc[i] == '매수':
            print('\033[95m')
            buy_count += 1
        else:
            print('\033[96m')
            sell_count += 1
        print(str(stock_data['macd_sign_with_volume'].iloc[i]) + " " + str(stock_data['날짜'].iloc[i]) + " " + str(stock_data['시간'].iloc[i]) + " 시가 : " + str(stock_data['시가'].iloc[i]))
print("\nsell_count : " + str(sell_count) + "\nbuy_count : " + str(buy_count))
