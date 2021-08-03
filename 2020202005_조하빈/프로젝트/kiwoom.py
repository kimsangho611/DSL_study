import sys
import time
import datetime
import numpy as np
import pandas as pd
from PyQt5.QtCore import QEventLoop
from PyQt5.QtWidgets import QApplication
from PyQt5.QAxContainer import QAxWidget

# 사용방법
# python 32비트에서 작동
# DEST에 원하는 코드와 옵션을 작성하여 실행
# False값이면 데이터 구하지 않는다.

# 대상 종목 코드(분봉 구간은 1,3,5,10,15,30,45,60)
DEST = {
    # 예시코드
    # '005930': {
    #     'MINUTE': [1,5,60],
    #     'DAILY': '20210720',
    #     'WEEKLY': False,
    #     'MONTHLY': '20210720'
    # },
    '004410': {
        'MINUTE': False,
        'DAILY': '20210801',
        'WEEKLY': '20210801'
    },
}


class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()
        self.smile = True

        # Api 컨트롤
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

        # 이벤트 루프 - 동기 처리에 사용
        self._login_eventloop = QEventLoop()
        self._receiveTr_eventloop = QEventLoop()

        ##### 이벤트 핸들러 연결 #####
        # 로그인 이벤트
        self.OnEventConnect.connect(self._loginHandler)

        # Tr 수신 이벤트
        self.OnReceiveTrData.connect(self._receiveTrHandler)

    ##### 이벤트 핸들러 정의 #####
    def _loginHandler(self, error):
        """ login 이벤트 핸들러 """
        if error == 0:
            print("로그인 성공!")
        else:
            print("로그인 실패...")
        self._login_eventloop.exit()

    def _receiveTrHandler(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext, nDataLength, sErrorCode, sMessage, sSplmMsg):
        """ Tr 수신 핸들러 """
        if sRQName in ['일봉조회', '분봉조회', '주봉조회', '월봉조회']:

            if sPrevNext == '2':
                self.remained_data = True
            else:
                self.remained_data = False

            time.sleep(0.3)
            data = self.dynamicCall(
                "GetCommDataEx(sTrCode,sRecordName)", sTrCode, sRecordName)
            self._li.extend(data)
            self._receiveTr_eventloop.exit()

    def _loading(self):
        if self.smile:
            print('\r＼^o^／', end='')
        else:
            print('\r／ovo＼', end='')
        self.smile = not self.smile

    ##### 메소드 #####
    def login(self) -> None:
        self.dynamicCall("CommConnect()")
        self._login_eventloop.exec()

    def getDailyCandle(self, code: str, date: str) -> pd.DataFrame:
        name = self.getName(code)
        if name:
            self._li = []
            self.dynamicCall("SetInputValue(sCode,value)", '종목코드', code)
            self.dynamicCall("SetInputValue(sDate,value)", '기준일자', date)
            self.dynamicCall("SetInputValue(division,int)", '수정주가구분', 1)
            self.dynamicCall(
                "CommRqData(sRQName,sTrCode,nPrevNext,sScreenNo)", '일봉조회', 'opt10081', 0, '0101')  # OnReceiveTrData 이벤트 발생
            self._receiveTr_eventloop.exec()

            while self.remained_data == True:
                self._loading()
                time.sleep(0.3)
                self.dynamicCall("SetInputValue(sCode,value)", '종목코드', code)
                self.dynamicCall("SetInputValue(sDate,value)", '기준일자', date)
                self.dynamicCall("SetInputValue(division,int)", '수정주가구분', 1)
                self.dynamicCall(
                    "CommRqData(sRQName,sTrCode,nPrevNext,sScreenNo)", '일봉조회', 'opt10081', 2, '0101')  # OnReceiveTrData 이벤트 발생
                self._receiveTr_eventloop.exec()

            self._df = pd.DataFrame(self._li, columns=[
                '', '종가', '거래량', '', '일자', '시가', '고가', '저가', '', '', '', '', '', '', '']).drop('', axis=1)
            self._df['종목코드'] = code
            self._df['종목명'] = name
            return self._df[['종목코드', '종목명', '일자',  '시가', '고가', '저가', '종가', '거래량']]

        else:
            print("종목코드가 잘못되었습니다.")
            return None

    def getMinuteCandle(self, code: str, period: int) -> pd.DataFrame:
        name = self.getName(code)
        if name:
            self._li = []
            self.dynamicCall("SetInputValue(sCode,value)", '종목코드', code)
            self.dynamicCall("SetInputValue(sDate,value)", '틱범위', period)
            self.dynamicCall("SetInputValue(division,int)", '수정주가구분', 1)
            self.dynamicCall(
                "CommRqData(sRQName,sTrCode,nPrevNext,sScreenNo)", '분봉조회', 'opt10080', 0, '0101')  # OnReceiveTrData 이벤트 발생
            self._receiveTr_eventloop.exec()

            while self.remained_data == True:
                time.sleep(0.3)
                self.dynamicCall("SetInputValue(sCode,value)", '종목코드', code)
                self.dynamicCall("SetInputValue(sDate,value)", '틱범위', period)
                self.dynamicCall("SetInputValue(division,int)", '수정주가구분', 1)
                self.dynamicCall(
                    "CommRqData(sRQName,sTrCode,nPrevNext,sScreenNo)", '분봉조회', 'opt10080', 2, '0101')  # OnReceiveTrData 이벤트 발생
                self._receiveTr_eventloop.exec()

            self._df = pd.DataFrame(self._li, columns=[
                '종가', '거래량', '일자', '시가', '고가', '저가', '', '', '', '', '', '', '']).drop('', axis=1)
            self._df['종목코드'] = code
            self._df['종목명'] = name

            self._df.loc[:, ['종가', '시가', '고가', '저가']] = self._df.loc[:, [
                '종가', '시가', '고가', '저가']].applymap(lambda x: abs(int(x)))
            return self._df[['종목코드', '종목명', '일자',  '시가', '고가', '저가', '종가', '거래량']]

        else:
            print("종목코드가 잘못되었습니다.")
            return None

    def getWeeklyCandle(self, code: str, date: str) -> pd.DataFrame:
        name = self.getName(code)
        if name:
            self._li = []
            self.dynamicCall("SetInputValue(sCode,value)", '종목코드', code)
            self.dynamicCall("SetInputValue(sDate,value)", '기준일자', date)
            self.dynamicCall("SetInputValue(division,int)", '수정주가구분', 1)
            self.dynamicCall(
                "CommRqData(sRQName,sTrCode,nPrevNext,sScreenNo)", '주봉조회', 'opt10082', 0, '0101')  # OnReceiveTrData 이벤트 발생
            self._receiveTr_eventloop.exec()

            while self.remained_data == True:
                time.sleep(0.3)
                self.dynamicCall("SetInputValue(sCode,value)", '종목코드', code)
                self.dynamicCall("SetInputValue(sDate,value)", '기준일자', date)
                self.dynamicCall("SetInputValue(division,int)", '수정주가구분', 1)
                self.dynamicCall(
                    "CommRqData(sRQName,sTrCode,nPrevNext,sScreenNo)", '주봉조회', 'opt10082', 2, '0101')  # OnReceiveTrData 이벤트 발생
                self._receiveTr_eventloop.exec()

            self._df = pd.DataFrame(self._li, columns=[
                '종가', '거래량', '', '일자', '시가', '고가', '저가', '', '', '', '', '', '', '']).drop('', axis=1)
            self._df['종목코드'] = code
            self._df['종목명'] = name
            return self._df[['종목코드', '종목명', '일자',  '시가', '고가', '저가', '종가', '거래량']]

        else:
            print("종목코드가 잘못되었습니다.")
            return None

    def getMonthlyCandle(self, code: str, date: str) -> pd.DataFrame:
        name = self.getName(code)
        if name:
            self._li = []
            self.dynamicCall("SetInputValue(sCode,value)", '종목코드', code)
            self.dynamicCall("SetInputValue(sDate,value)", '기준일자', date)
            self.dynamicCall("SetInputValue(division,int)", '수정주가구분', 1)
            self.dynamicCall(
                "CommRqData(sRQName,sTrCode,nPrevNext,sScreenNo)", '월봉조회', 'opt10083', 0, '0101')  # OnReceiveTrData 이벤트 발생
            self._receiveTr_eventloop.exec()

            while self.remained_data == True:
                time.sleep(0.3)
                self.dynamicCall("SetInputValue(sCode,value)", '종목코드', code)
                self.dynamicCall("SetInputValue(sDate,value)", '기준일자', date)
                self.dynamicCall("SetInputValue(division,int)", '수정주가구분', 1)
                self.dynamicCall(
                    "CommRqData(sRQName,sTrCode,nPrevNext,sScreenNo)", '월봉조회', 'opt10083', 2, '0101')  # OnReceiveTrData 이벤트 발생
                self._receiveTr_eventloop.exec()

            self._df = pd.DataFrame(self._li, columns=[
                '종가', '거래량', '', '일자', '시가', '고가', '저가', '', '', '', '', '', '', '']).drop('', axis=1)
            self._df['종목코드'] = code
            self._df['종목명'] = name
            return self._df[['종목코드', '종목명', '일자',  '시가', '고가', '저가', '종가', '거래량']]

        else:
            print("종목코드가 잘못되었습니다.")
            return None

    def getName(self, code) -> str:
        time.sleep(0.3)
        return self.dynamicCall("GetMasterCodeName(sCode)", code)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    kiwoom = Kiwoom()
    kiwoom.login()

    for code, options in DEST.items():
        name = kiwoom.getName(code)
        if name:
            if options.get('MINUTE'):
                for period in options.get('MINUTE'):
                    print(
                        f'{name}({code}) {period}분봉 가져오는 중...')
                    start = time.time()
                    kiwoom.getMinuteCandle(code, period).to_excel(
                        f'{name}({code})_{period}분봉.xlsx')
                    stop = time.time()
                    print(
                        f'{name}({code}) {period}분봉 완료!')
                    print(
                        f'걸린시간 {str(datetime.timedelta(seconds=stop-start)).split(".")[0]}\n')

            if options.get('DAILY'):
                print(
                    f'{name}({code}) 일봉 가져오는 중...')
                start = time.time()
                kiwoom.getDailyCandle(code, options.get(
                    'DAILY')).to_excel(f'{name}({code})_일봉.xlsx')
                stop = time.time()
                print(
                    f'\r{name}({code}) 일봉 완료!')
                print(
                    f'걸린시간 {str(datetime.timedelta(seconds=stop-start)).split(".")[0]}\n')

            if options.get('WEEKLY'):
                print(
                    f'{name}({code}) 주봉 가져오는 중...')
                start = time.time()
                kiwoom.getWeeklyCandle(code, options.get(
                    'WEEKLY')).to_excel(f'{name}({code})_주봉.xlsx')
                stop = time.time()
                print(
                    f'{name}({code}) 주봉 완료!')
                print(
                    f'걸린시간 {str(datetime.timedelta(seconds=stop-start)).split(".")[0]}\n')

            if options.get('MONTHLY'):
                print(
                    f'{name}({code}) 월봉 가져오는 중...')
                start = time.time()
                kiwoom.getMonthlyCandle(code, options.get(
                    'MONTHLY')).to_excel(f'{name}({code})_월봉.xlsx')
                stop = time.time()
                print(
                    f'{name}({code}) 월봉 완료!')
                print(
                    f'걸린시간 {str(datetime.timedelta(seconds=stop-start)).split(".")[0]}\n')
        else:
            print(f'잘못된 종목코드({code})')
