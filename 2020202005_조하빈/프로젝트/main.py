import numpy as np
import pandas as pd

# 경로설정
location = "C:\\Users\\82105\\문서\\조하빈\\주식스터디\\DSL_study\\강의자료\\여름방학\\week2\\data\\컴투스.csv"

df_raw = pd.read_csv(location, names=[
    '종목명', '종목코드', '거래일', '거래시각', '시가', '고가', '저가', '종가', '거래량'], header=None, encoding='CP949')

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
        PMF = 0
        NMF = 0
        for j in range(0, 14):
            if df.loc[i+j, '평균가격'] > df.loc[i+j+1, '평균가격']:  # 양인 경우
                PMF += df.loc[i+j, 'mf']
            elif df.loc[i+j, '평균가격'] < df.loc[i+j+1, '평균가격']:  # 음인 경우
                NMF += df.loc[i+j, 'mf']
        if NMF == 0:
            df.loc[i, 'MFI'] = 100
        else:
            MFR = PMF/NMF
            df.loc[i, 'MFI'] = 100-100/(1+MFR)

df.to_excel('df.xlsx')
print(df.head(40))


# # MFI 추가
# mfi_period = 14

# pmf = []
# nmf = []
# for i in range(0, len(df)-1):
#     if df.loc[i, '평균가격'] > df.loc[i+1, '평균가격']:  # 양인 경우
#         pmf.append(df.loc[i, 'mf'])
#         nmf.append(0)
#     elif df.loc[i, '평균가격'] < df.loc[i+1, '평균가격']:  # 음인 경우
#         nmf.append(df.loc[i, 'mf'])
#         pmf.append(0)
#     else:
#         pmf.append(0)
#         nmf.append(0)

# print("mfi 계산중...")
# for i in range(0, 100):
#     if i > len(df)-mfi_period:
#         continue
#     else:
#         PMF = sum(pmf[i:i+mfi_period])
#         NMF = sum(nmf[i:i+mfi_period])
#         df.loc[i, 'MFI'] = 100*PMF/(PMF+NMF)

# print(df)
