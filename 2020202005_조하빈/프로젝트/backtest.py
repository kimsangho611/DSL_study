import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from mplfinance.original_flavor import candlestick2_ohlc


class Indicator:
    def __init__(self, location: str):
        self.__data = pd.DataFrame(pd.read_excel(location, index_col=0))

    def mfi(self, period: int = 14):
        avg = (self.__data['고가']+self.__data['저가']+self.__data['종가'])/3  # 평균가격
        mf = self.__data['거래량']*avg  # mf
        evaluation = pd.Series(['positive' if avg.iloc[i] > avg.iloc[i+1] else (
            'negative' if avg.iloc[i] < avg.iloc[i+1] else 'same') for i in range(len(avg)-1)])  # 이전 봉 대비 상승/하락/유지 정보

        # TODO: 만약 평균가격이 14일(기준기간)동안 같은 값으로 유지되면...?
        mfi = []
        for i in range(len(evaluation)-period):
            pmf = mf.iloc[i:i+period].loc[evaluation == 'positive'].sum()
            nmf = mf.iloc[i:i+period].loc[evaluation == 'negative'].sum()
            if not nmf and not pmf:
                mfi.append(mfi[-1])
            else:
                mfi.append(100*pmf/(pmf+nmf))

        self.__data['MFI'] = pd.Series(mfi)

    def to_dataframe(self) -> pd.DataFrame: return self.__data

    def to_excel(self, name):
        self.__data.to_excel(name)


class BackTest:
    def __init__(self, data: pd.DataFrame, name):
        self.__name = name
        self.__data: pd.DataFrame = data  # 차트 봉 데이터
        self.__data['signal'] = np.nan
        self.__SEED_MONEY: int = 10000000  # 초기자금

        # 키움증권 영웅문4 기준으로 수수료 책정
        # https://www.kiwoom.com/h/help/fee/VHelpStockFeeView
        self.__BUY_COMMISSION = 0.00015+0.0000519496  # 위탁수수료+유관기관수수료
        self.__SELL_COMMISSION = 0.00015+0.0000519496 + \
            0.0008+0.0015  # 위탁수수료+유관기관수수료+거래세+농어촌특별세

        self.__current_money: int = self.__SEED_MONEY

        self.__stock = {  # 보유중인 주식
            '평단가': 0,
            '보유수량': 0
        }
        self.__log = []  # 매매 기록

    def __get_quantity(self) -> int: return self.__stock['보유수량']

    def __get_avg(self) -> int: return self.__stock['평단가']

    def __get_asset(self) -> int:
        return self.__current_money + self.__stock['보유수량']*self.__stock['평단가']

    def __buy(self, data: pd.Series, money):
        # TODO 시가 vs 종가 vs 평균가?
        if money > self.__current_money:
            print('매수실패: 금액 부족')
            return

        # 매수 signal 처리
        self.__data.loc[int(data.name), 'signal'] = 'buy'

        # 매수
        count = 0  # 주문수량
        while money > 0:
            count = count+1
            money = money-data['시가']*(1+self.__BUY_COMMISSION)
            self.__current_money = self.__current_money - \
                data['시가']*(1+self.__BUY_COMMISSION)

        if money < 0:
            count = count-1
            money = money+data['시가']*(1+self.__BUY_COMMISSION)
            self.__current_money = self.__current_money + \
                data['시가']*(1+self.__BUY_COMMISSION)

        self.__stock['평단가'] = (
            self.__stock['평단가']*self.__stock['보유수량']+count*data['시가'])/(self.__stock['보유수량']+count)
        self.__stock['보유수량'] = self.__stock['보유수량']+count

        # log
        self.__log.append({
            '구분': '매수',
            '일자': str(data['일자']),
            '가격': data['시가'],
            '수량': count,
            '평단가': self.__get_avg(),
            '보유수량': self.__get_quantity(),
            '보유현금': self.__current_money,
            '총자산': self.__get_asset()
        })

    def __sell(self, data, ratio, mode='매도'):
        if not self.__stock['보유수량']:
            print('매도실패: 보유수량 없음')
            return

        # 매수 signal 처리
        self.__data.loc[int(data.name), 'signal'] = 'sell'

        price = self.__stock['평단가']
        sell_quantity = int(self.__stock['보유수량']*ratio)
        self.__stock['보유수량'] = self.__stock['보유수량']-sell_quantity
        self.__current_money = self.__current_money + \
            data['시가']*(1-self.__SELL_COMMISSION)*sell_quantity

        self.__log.append({
            '구분': mode,
            '일자': str(data['일자']),
            '구매가': price,
            '판매가': data['시가'],
            '수량': sell_quantity,
            '승패': 'WIN' if data['시가']*(1-self.__SELL_COMMISSION) > price else 'LOSE',
            '수익률': data['시가']/price-1,
            '평단가': self.__get_avg(),
            '보유수량': self.__get_quantity(),
            '보유현금': self.__current_money,
            '총자산': self.__get_asset()
        })

    # def __sell_all(self, data: pd.Series):
    #     # TODO 시가 vs 종가 vs 평균가?
    #     if not self.__stock_list:
    #         print('매도실패: 보유주식 없음')
    #     for stock in self.__stock_list:
    #         self.__current_money = self.__current_money + \
    #             data['시가']*(1-self.__SELL_COMMISSION)*stock['수량']

    #         self.__log.append({
    #             '구분': '전체매도',
    #             '일자': str(data['일자']),
    #             '구매가': stock['매수가'],
    #             '판매가': data['시가'],
    #             '수량': stock['수량'],
    #             '승패': 'WIN' if data['시가']*(1-self.__SELL_COMMISSION) > stock['매수가'] else 'LOSE',
    #             '평단가': self.__get_avg(),
    #             '보유수량': self.__get_quantity(),
    #             '보유현금': self.__current_money,
    #             '총자산': self.__get_asset()
    #         })

    #     self.__stock_list.clear()

    def __check_lossline(self, criteria, data: pd.Series):
        """ 손절라인 """
        if not self.__stock['보유수량']:  # 보유주식 없는 경우
            return

        if (data['시가']/self.__stock['평단가']-1) < criteria:
            self.__sell(data, 1, '손절매도')

    def log(self, name):
        with open(name, 'w') as f:
            for i in self.__log:
                for x, y in i.items():
                    f.write(f'{x}: {y}\n')
                f.write('\n')
            f.write(str((self.__get_asset()/self.__SEED_MONEY-1)*100)+'\n')

    def trade_mfi(self):
        self.__current_money = self.__SEED_MONEY
        index = len(self.__data['MFI'])-2
        while index > 0:
            self.__check_lossline(-0.02, self.__data.loc[index-1])
            prev_mfi = self.__data.loc[index+1, 'MFI']
            current_mfi = self.__data.loc[index, 'MFI']

            # 매수: mfi가 20선을 상향돌파 시 시드머니의 25퍼센트 투자
            if prev_mfi < 20 and current_mfi >= 20:
                self.__buy(self.__data.loc[index-1], self.__SEED_MONEY*0.5)

            # 매도: mfi가 80선을 하향돌파 시 보유주식 전체 매도
            elif prev_mfi > 80 and current_mfi <= 80:
                self.__sell(self.__data.loc[index-1], 1)

            index = index-1

    def trade_mfi_divergence(self, period=14):

        pass

    def trade_buy_and_hold(self):
        self.__buy(self.__data.iloc[-1], self.__SEED_MONEY)
        self.__sell(self.__data.iloc[0], 1)

    def evaluate(self):
        print((self.__get_asset()/self.__SEED_MONEY-1)*100)

    def reset(self):
        self.__current_money = self.__SEED_MONEY
        self.__stock = {'평단가': 0, '보유수량': 0}
        self.__log.clear()

    def test(self):  # 차트 표시
        fig: plt.figure = plt.figure(figsize=(20, 10))
        ax = fig.add_subplot(111)

        ax.xaxis.set_major_locator(ticker.MaxNLocator(20))

        ax.set_title('mfi', fontsize=15)
        ax.set_ylabel("price")
        ax.set_xlabel("Date Time")

        _date = list(map(str, self.__data['일자']))
        _date.reverse()

        _li1 = list(self.__data['시가'])
        _li1.reverse()

        _li2 = list(self.__data['고가'])
        _li2.reverse()

        _li3 = list(self.__data['저가'])
        _li3.reverse()

        _li4 = list(self.__data['종가'])
        _li4.reverse()

        # 봉차트
        candlestick2_ohlc(ax, _li1, _li2, _li3, _li4,
                          width=0.5, colorup='r', colordown='b')

        # 매수: 세모, 매도: 별
        for i in range(len(self.__data['signal'])):

            if self.__data.loc[i, 'signal'] == 'buy':
                ax.scatter(len(self.__data['signal'])-1-i,
                           self.__data.loc[i, '시가'], marker='^', alpha=1, color='lime')
            elif self.__data.loc[i, 'signal'] == 'sell':
                ax.scatter(len(self.__data['signal'])-1-i,
                           self.__data.loc[i, '시가'], marker='*', alpha=1, color='black')

        ax.set_xticks([i for i in range(0, len(_date))])
        ax.set_xticklabels(_date, rotation=30)
        ax.legend()
        plt.show()

    def to_dataframe(self):
        return self.__data


if __name__ == '__main__':
    df = Indicator('lg전자/lg_2년치일봉.xlsx')
    df.mfi()

    backtest = BackTest(df.to_dataframe(), 'lg전자')
    backtest.trade_mfi()
    backtest.to_dataframe().to_excel('테스트.xlsx')
    backtest.log('lg_2년치일봉_손절2%.txt')

    backtest.test()
    # backtest.reset()

    # backtest.evaluate()


# 폭락에 휩쓸리고 매수 -> 손해
# 손절라인 적용 5%
# 분할매매 적용
# 이평선 골든크로스 데드크로스 추가해 매수/매도 타이밍 추가?
# 윌리엄스R

# divergence
