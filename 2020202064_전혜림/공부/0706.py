from pandas import Series, DataFrame
import pandas as pd
import numpy as np

data = "C:\\Users\\Hyerim\\DSL_study\\강의자료\\여름방학\\week2\\data\\컴투스.csv"
df_data = pd.read_csv(data, encoding='cp949', header = None,  names = ['종목명', '종목코드', '날짜', '시간', '시가', '고가', '저가', '종가', '거래량'])

print(df_data.head())

'''print("\n\n거래량이 가장 많은 날")
print(df_data.iloc[df_data["거래량"].argmax()])

df_data["등락률"] = (df_data["종가"] - df_data["종가"].shift(1)) * 100 / df_data["종가"].shift(1)

print(df_data.iloc[df_data["등락률"].argmax()])

print("\n\n최고로 많이 떨어진 날")
print(df_data.iloc[df_data["등락률"].argmin()])

print("\n\n최고로 많이 오른날")
print(df_data.iloc[df_data["등락률"].argmax()])'''

#컴투스 종목 5일 이동평균선 구하기
data['종가'].rolling(widow = 5).mean()[:20]

ma5_list = []
for i in range(4) : ma5_list.append(0)
for i in range(4, len(data['종가'])) :
    ma5 = data['종가'].iloc[i - 4: i + 1].mean()
    ma5_list.append(ma5)
data['5일 이평선'] = np.array(ma5_list)

