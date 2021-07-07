from pandas import Series, DataFrame
import pandas as pd
import numpy as np

data = "C://Users//bjybs//Desktop//JP//DSL_study//강의자료//여름방학//week2//data//컴투스.csv"
df_data = pd.read_csv(data, encoding='cp949', header = None,  names = ['종목명', '종목코드', '날짜', '시간', '시가', '고가', '저가', '종가', '거래량'])

print(df_data)

df_data['sma5'] = df_data['종가'].rolling(5).mean()


print(df_data)
