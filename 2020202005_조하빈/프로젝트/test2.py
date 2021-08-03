import FinanceDataReader as fdr
import pandas as pd
import time
import matplotlib.pyplot as plt

df=fdr.DataReader('078340','2020')
chart=df

ma5=pd.DataFrame(chart['Close'].rolling(window=5).mean())
ma20=pd.DataFrame(chart['Close'].rolling(window=20).mean())
ma60=pd.DataFrame(chart['Close'].rolling(window=60).mean())
ma120=pd.DataFrame(chart['Close'].rolling(window=120).mean())
chart.insert(len(chart.columns), '5일', ma5)
chart.insert(len(chart.columns), '20일', ma20)
chart.insert(len(chart.columns), '60일', ma60)
chart.insert(len(chart.columns), '120일', ma120)

fig=plt.figure(figsize=(20, 10))
pr_line=plt.subplot2grid((4,4), (0,0), rowspan=3, colspan=4,)
vol_bar=plt.subplot2grid((4,4), (3,0), rowspan=1, colspan=4)
x=chart.index.strftime('%m.%d')

pr_line.plot(chart.index, chart['5일'], label='MA5')
pr_line.plot(chart.index, chart['20일'], label='MA20')
pr_line.plot(chart.index, chart['60일'], label='MA60')
pr_line.plot(chart.index, chart['120일'], label='MA120',color='purple' )
pr_line.bar(chart.index, height=chart['Close']-chart['Open'], bottom=chart['Open'], width=1, color=list(map(lambda c: 'red' if c>0 else 'blue', chart['Change'])))
pr_line.vlines(chart.index, chart['Low'], chart['High'], color=list(map(lambda c: 'red' if c>0 else 'blue', chart['Change'])))

vol_bar.bar(x, df['Volume'])

plt.title('컴투스')
plt.show()