import win32com.client
import time
import os
from datetime import datetime, timedelta

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
    stockName = "컴투스"
    d = DataCollection(stockName, 20210101, 20210714, store_path)
    d.run('분봉', 1)
    """