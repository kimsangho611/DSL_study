import win32com.client
import time
from datetime import datetime, timedelta

class DataCollection:
    def __init__(self, startDay, endDay, StoreLocation):
        self.StockChart = win32com.client.Dispatch("CpSysDib.StockChart")
        self.CpStockCode = win32com.client.Dispatch("CpUtil.CpStockCode")
        self.startDay = startDay
        self.endDay = endDay
        self.StoreLocation = StoreLocation

    def CollectDay(self):
        pass

    def CollectMinute(self, StockName, StockCode, chart='m', type_value=None, timeperiod=5, ReqCount=2000):
        self.StockChart.SetInputValue(0, StockCode)
        self.StockChart.SetInputValue(5, type_value) # 어떤 데이터를 받을 지
        self.StockChart.SetInputValue(6, ord(chart)) # 차트 종류
        self.StockChart.SetInputValue(9, ord('1')) # 수정주가 사용
        if chart == 'm':
            self.StockChart.SetInputValue(1, ord('2'))  # 개수로 요청
            self.StockChart.SetInputValue(4, ReqCount)  # 몇개의 데이터를 수신할 지
            self.StockChart.SetInputValue(7, timeperiod)  # 몇 분봉으로 받을지
        elif chart == 'D':
            self.StockChart.SetInputValue(1, ord('1'))  # 기간으로 요청
            self.StockChart.SetInputValue(2, self.endDay)
            self.StockChart.SetInputValue(3, self.startDay)

        self.StockChart.BlockRequest()
        time.sleep(0.25)

        receive = self.StockChart.GetHeaderValue(3)
        with open(self.StoreLocation.format(StockName), 'w') as f:
            if chart == 'D':
                for i in range(receive):
                    f.write("{},{},{},{},{},{},{},{}\n".format(
                        StockName, StockCode,
                        self.StockChart.GetDataValue(0, i),
                        self.StockChart.GetDataValue(2, i),
                        self.StockChart.GetDataValue(3, i),
                        self.StockChart.GetDataValue(4, i),
                        self.StockChart.GetDataValue(5, i),
                        self.StockChart.GetDataValue(6, i)
                    ))
            elif chart == 'm':
                for i in range(receive):
                    t = self.StockChart.GetDataValue(0, i)
                    if (t <= self.startDay) and (t >= self.endDay):
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
                    self.StockChart.BlockRequest()
                    receive = self.StockChart.GetHeaderValue(3)

                    for i in range(receive):
                        t = self.StockChart.GetDataValue(0, i)
                        if (t <= self.startDay) and (t >= self.endDay):
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

if __name__=='__main__':
    stockName = "컴투스"
    d = DataCollection(20100101, 20210512, r"C:\Users\kimsangho\Desktop\{}.csv")
    d.CollectMinute(StockName=stockName,StockCode = d.CpStockCode.NameToCode(stockName),chart='D', type_value=[0, 1, 2, 3, 4, 5, 8], timeperiod=5, ReqCount=2000)