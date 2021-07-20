import sys
import time
from PyQt5.QtCore import QEventLoop
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QAxContainer import *

# set CONDA_FORCE_32BIT=1


class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()

        # Api 컨트롤
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

        # 이벤트 루프 - 동기 처리에 사용
        self.login_eventloop = QEventLoop()
        self.receiveTr_eventloop = QEventLoop()

        ##### 이벤트 핸들러 연결 #####
        # 로그인 이벤트
        self.OnEventConnect.connect(self.loginHandler)

        # Tr 수신 이벤트
        self.OnReceiveTrData.connect(self.receiveTrHandler)

    ##### 이벤트 핸들러 정의 #####
    def loginHandler(self, error):
        """ login 이벤트 핸들러 """
        if error == 0:
            print("로그인 성공!")
        else:
            print("로그인 실패...")
        self.login_eventloop.exit()

    def receiveTrHandler(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext, nDataLength, sErrorCode, sMessage, sSplmMsg):
        """ Tr 수신 핸들러 """
        if sRQName == 'opt10001_req':
            name = self.dynamicCall(
                "GetCommData(sTrCode, sRQName, index, dest)", sTrCode, sRQName, 0, '종목명')
            print(name)
            self.receiveTr_eventloop.exit()

        elif sRQName == '일봉조회':
            cnt = self.dynamicCall("GetRepeatCnt(tr,code)", sTrCode, sRQName)
            if sPrevNext == '2':
                self.remained_data = True
            else:
                self.remained_data = False
            for i in range(cnt):
                date = self.dynamicCall(
                    "GetCommData(sTrCode, sRQName, index, dest)", sTrCode, sRQName, i, '일자').strip()
                open = self.dynamicCall(
                    "GetCommData(sTrCode, sRQName, index, dest)", sTrCode, sRQName, i, '시가').strip()
                high = self.dynamicCall(
                    "GetCommData(sTrCode, sRQName, index, dest)", sTrCode, sRQName, i, '고가').strip()
                low = self.dynamicCall(
                    "GetCommData(sTrCode, sRQName, index, dest)", sTrCode, sRQName, i, '저가').strip()
                close = self.dynamicCall(
                    "GetCommData(sTrCode, sRQName, index, dest)", sTrCode, sRQName, i, '현재가').strip()  # 현재가=종가
                volume = self.dynamicCall(
                    "GetCommData(sTrCode, sRQName, index, dest)", sTrCode, sRQName, i, '거래량').strip()
                print(i, date, open, high, low, close, volume)
                self.receiveTr_eventloop.exit()

    ##### 메소드 #####
    def login(self):
        self.dynamicCall("CommConnect()")
        self.login_eventloop.exec()

    def getDailyCandle(self, code, date):
        if self.dynamicCall("GetMasterCodeName(sCode)", code):
            self.dynamicCall("SetInputValue(sCode,value)", '종목코드', code)
            self.dynamicCall("SetInputValue(sDate,value)", '기준일자', date)
            self.dynamicCall("SetInputValue(division,int)", '수정주가구분', 0)
            self.dynamicCall(
                "CommRqData(sRQName,sTrCode,nPrevNext,sScreenNo)", '일봉조회', 'opt10081', 0, '0101')
            self.receiveTr_eventloop.exec()

            while self.remained_data == True:
                time.sleep(0.5)
                self.dynamicCall("SetInputValue(sCode,value)", '종목코드', code)
                self.dynamicCall("SetInputValue(sDate,value)", '기준일자', date)
                self.dynamicCall("SetInputValue(division,int)", '수정주가구분', 0)
                self.dynamicCall(
                    "CommRqData(sRQName,sTrCode,nPrevNext,sScreenNo)", '일봉조회', 'opt10081', 2, '0101')
                self.receiveTr_eventloop.exec()

        else:
            print("종목코드가 잘못되었습니다.")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    kiwoom = Kiwoom()
    kiwoom.show()
    kiwoom.login()

    # opt10081: 주식일봉차트조회요청
    kiwoom.getDailyCandle('004410', '20210719')
