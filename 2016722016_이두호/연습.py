import pandas as pd
import numpy as np
import datetime

comission_buy = 1.0016
comission_sell = 0.0025

class trader:
    def __init__(self, Money):
        self.__Money = Money #자본금 세팅
        self.__bat_limitation =  self.__Money * 0.5
        self.__bat_size = self.__bat_limitation * 0.02
        self.__numStock = 0
        self.__total_bat = 0
    
    def reSetting(self):
        self.__bat_limitation =  self.__Money * 0.5 #배팅한도는 총자산의 50%
        self.__bat_size = self.__bat_limitation * 0.02  #첫배팅은 배팅한도의 2%
        self.__numStock = 0
        self.__total_bat = 0
    
    def buyStock(self,stock_price):
        newStock = 0  
        if self.__Money > self.__bat_limitation and self.__Money > 0:            
            newStock = int(self.__bat_size / stock_price)
            self.__Money -= (stock_price * newStock) * comission_buy
            self.__numStock += newStock
            self.__total_bat += self.__bat_size
            self.__bat_size *= 1.3 #1.3배씩 물타기
            
    
    def sellStock(self, stock_price):
        if self.__numStock > 0 :
            self.__Money += (stock_price * self.__numStock)*(1-comission_sell) 
            self.reSetting()

    def lossCut(self, stock_price):
        if self.__total_bat - (stock_price * self.__numStock) > self.__Money * 0.04:
            print("손절")
            self.sellStock(stock_price)
            self.reSetting()
            
    def earningCut(self,stock_price):
        if stock_price * self.__numStock > self.__total_bat * 1.08:
            print("익절")
            self.sellStock(stock_price)
            self.reSetting()
            
    def Show_Money(self):
        print(self.__Money)
    
    def Show_numStock(self):
        print(self.__numStock)
    
    def Show_limit(self):
        print(self.__bat_limitation)

data = pd.read_csv("./고려제약.csv", encoding= 'CP949', header = None, names = ['종목명', '종목코드', '날짜', '시간', '시가', '고가', '저가', '종가','거래량'])

ma_20 = data['종가'].rolling(window = 20).mean()
bol_upper = ma_20 + 2*data['종가'].rolling(window=20).std()
bol_down = ma_20 - 2*data['종가'].rolling(window=20).std()

data['20이평'] = ma_20
data['볼린저 상단'] = bol_upper
data['볼린저 하단'] = bol_down

DUHO = trader(100000000)

##자본금##
DUHO.Show_Money

for i in reversed(range(len(bol_down))):
    stock_price = data['시가'].iloc[i]
    
    
    if stock_price < bol_down[i] + (ma_20[i] - bol_down[i]) * 0.1:
        DUHO.buyStock(stock_price)
    DUHO.lossCut(stock_price)
    DUHO.earningCut(stock_price)
    
    DUHO.Show_Money()
    DUHO.Show_numStock()
    DUHO.Show_limit()
    
DUHO.sellStock(stock_price)

##거래 후 자본금##
DUHO.Show_Money()