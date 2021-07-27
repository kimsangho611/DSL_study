import numpy as np
import pandas as pd

location = "C:\\Users\\82105\\문서\\조하빈\\주식스터디\\DSL_study\\강의자료\\여름방학\\week2\\data\\컴투스.csv"

# df_raw = pd.read_csv(location, names=[
#     '종목명', '종목코드', '거래일', '거래시각', '시가', '고가', '저가', '종가', '거래량'], header=None, encoding='CP949')

df_raw = pd.read_excel(
    'LG전자(066570)_일봉.xlsx', index_col=0)
df = pd.DataFrame(df_raw, copy=True)

df['평균가격'] = (df['고가']+df['저가']+df['종가'])/3
df['mf'] = df['거래량']*df['평균가격']
df['MFI'] = np.nan
print(df)

# MFI 추가
mfi_period = 14
for i in range(0, len(df)):
    if i >= len(df)-mfi_period:
        continue
    else:
        pmf = 0
        nmf = 0
        for j in range(0, 14):
            if df.loc[i+j, '평균가격'] > df.loc[i+j+1, '평균가격']:  # 양인 경우
                pmf += df.loc[i+j, 'mf']
            elif df.loc[i+j, '평균가격'] < df.loc[i+j+1, '평균가격']:  # 음인 경우
                nmf += df.loc[i+j, 'mf']
        if nmf == 0:
            df.loc[i, 'MFI'] = 100
        else:
            mfr = pmf/nmf
            df.loc[i, 'MFI'] = 100-100/(1+mfr)
    print(i, len(df))

df.to_excel('df.xlsx')
print(df.head(40))
