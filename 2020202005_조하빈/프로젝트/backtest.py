import numpy as np
import pandas as pd


class Indicator:
    def __init__(self, data: pd.DataFrame):
        self.__data = data

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
            mfi.append(100*pmf/(pmf+nmf))

        self.__data['MFI'] = pd.Series(mfi)
        # mfi=[mf.iloc[:period]]
        # print(avg, evaluation)

    def to_dataframe(self) -> pd.DataFrame: return self.__data


class BackTest:
    def __init__(self, data: pd.DataFrame):
        self.__data: pd.DataFrame = data  # 차트 봉 데이터
        self.__SEED_MONEY: int = 10000000  # 초기자금

        # 키움증권 영웅문4 기준으로 수수료 책정
        # https://www.kiwoom.com/h/help/fee/VHelpStockFeeView
        self.__BUY_COMMISSION = 0.00015+0.0000519496  # 위탁수수료+유관기관수수료
        self.__SELL_COMMISSION = 0.00015+0.0000519496 + \
            0.0008+0.0015  # 위탁수수료+유관기관수수료+거래세+농어촌특별세

        self.__current_money: int = self.__SEED_MONEY

        self.__stock_list = []  # 보유중인 주식
        self.__log = []  # 매매 기록

    def __buy(self, data: pd.Series, money):
        # TODO 시가 vs 종가 vs 평균가?
        if money > self.__current_money:
            print('매수실패: 금액 부족')
            return

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

        self.__stock_list.append({
            '매수가': data['시가'],
            '수량': count
        })
        self.__log.append({
            '구분': '매수',
            '일자': str(data['일자']),
            '가격': data['시가'],
            '수량': count,
            '승패': ''
        })

        print(
            f"""
'구분': '매수',
'일자': {str(data['일자'])},
'가격': {data['시가']},
'수량': {count},
'승패': ''
'남은캐쉬': {self.__current_money}
"""
        )

    def __sell_all(self, data: pd.Series):
        # TODO 시가 vs 종가 vs 평균가?
        if not len(self.__stock_list):
            print('매도실패: 보유주식 없음')
        for stock in self.__stock_list:
            self.__current_money = self.__current_money + \
                data['시가']*(1-self.__SELL_COMMISSION)*stock['수량']

            self.__log.append({
                '구분': '매도',
                '일자': str(data['일자']),
                '가격': data['시가'],
                '수량': stock['수량'],
                '승패': 'WIN' if data['시가']*(1-self.__SELL_COMMISSION) > stock['매수가'] else "LOSE"
            })

            print(
                f"""
'구분': '매도',
'일자': {str(data['일자'])},
'구매가/판매가': {stock['매수가']}/{data['시가']},
'수량': {stock['수량']},
'승패': {'WIN' if data['시가']*(1-self.__SELL_COMMISSION) > stock['매수가'] else "LOSE"}
'남은캐쉬': {self.__current_money}
"""
            )

        self.__stock_list.clear()

    def trade_by_mfi(self):
        index = len(self.__data['MFI'])-2

        while index > 0:
            prev_mfi = self.__data.loc[index+1, 'MFI']
            current_mfi = self.__data.loc[index, 'MFI']

            # 매수: mfi가 20선을 상향돌파 시 시드머니의 25퍼센트 투자
            if prev_mfi < 20 and current_mfi >= 20:
                self.__buy(self.__data.loc[index-1], self.__SEED_MONEY*0.25)

            # 매도: mfi가 80선을 하향돌파 시 보유주식 전체 매도
            elif prev_mfi > 80 and current_mfi <= 80:
                self.__sell_all(self.__data.loc[index-1])

            index = index-1

    def evaluate(self):
        print(self.__current_money)


if __name__ == '__main__':
    df = Indicator(pd.DataFrame(pd.read_excel(
        'lg_2년치일봉.xlsx', index_col=0)))

    df.mfi()

    backtest = BackTest(df.to_dataframe())
    backtest.trade_by_mfi()
    backtest.evaluate()


# 폭락에 휩쓸리고 매수 -> 손해
# 손절라인 적용?
# 분할매매 적용?
# 이평선 골든크로스 데드크로스 추가해 매수/매도 타이밍 추가?

# divergence
