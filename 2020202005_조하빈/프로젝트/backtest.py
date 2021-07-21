import numpy as np
import pandas as pd


# 구매가는 평균가격으로 가정
# 구매는 1주씩만 하는걸로 가정
def mfi(data: pd.DataFrame):
    """ mfi """
    stock_list = []  # 보유한 주식의 매수 가격들
    profit = 0
    current_index = len(data)-16

    f = open("mfi_backtest.txt", 'w')
    while(current_index):
        previous_mfi = data.loc[current_index-1, 'MFI']
        current_mfi = data.loc[current_index, 'MFI']

        # 20 상향돌파시 매수
        if(previous_mfi <= 20 and current_mfi > 20):
            stock_list.append(data.loc[current_index, '평균가격'])

        # 80 하향돌파시 매도
        if(previous_mfi >= 80 and current_mfi < 80 and len(stock_list)):
            gain = np.average(stock_list)/data.loc[current_index, '평균가격']-1
            print(f"{data.loc[current_index, '거래일']} \
                    {data.loc[current_index, '거래시각']} \
                    {gain}")

            f.write(f"{data.loc[current_index, '거래일']} \
                    {data.loc[current_index, '거래시각']} \
                    {gain}\n")

            profit = profit+gain
            stock_list.clear()

        current_index = current_index-1
    f.write(str(profit))
    f.close()


df = pd.DataFrame(pd.read_excel('df.xlsx', index_col=0))
df['MFI'] = df['MFI'].shift(1)

mfi(df)
