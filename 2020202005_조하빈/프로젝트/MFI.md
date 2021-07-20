# MFI 지표

## MFI 지표란?
Money Flow Index의 준말  
RSI와 비슷하며 RSI에 거래량을 추가한 지수  
자산의 과매도, 과매수를 식별하는데 활용  

---

## MFI 계산
__평균가격__ = (고가 + 저가 + 종가)/3  
__MF__ = 거래량 * 평균가격  
__PMF__(Positive Money Flow) : 기준기간동안의 양(평균가격이 이전 대비 상승)의 MF의 합  
__NMF__(Negative Money Flow) : 기준기간동안의 음(평균가격이 이전 대비 하락)의 MF의 합  
__MFR__(Money Flow Ratio) = PMF/NMF  
__MFI__ = MFR/(1+MFR) = PMF/(PMF+NMF)

---

## MFI 활용
MFI 지표는 다음처럼 해석한다.  
MFI > 80 : 과매수  
MFI < 20 : 과매도  

생각해본 활용 방법
1. Under 20: 매수, Over 80: 매도 
2. divergence -> 추세 전환
3. 하향돌파, 상향돌파에서 순간 기울기 개념 추가 -> 기울기에 따라 분할 매매
---