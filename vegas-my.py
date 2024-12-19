import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 下载数据
symbol = "AAPL"
start_date = "2022-01-01"
end_date = "2024-12-17"
data = yf.download(symbol, start=start_date, end=end_date)

if data.empty:
    print("数据下载失败或数据为空")
else:
    print("数据下载成功")

# 计算EMA
def ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

data['EMA_12'] = ema(data['Close'], 12)
data['EMA_144'] = ema(data['Close'], 144)
data['EMA_169'] = ema(data['Close'], 169)
data['EMA_576'] = ema(data['Close'], 576)
data['EMA_676'] = ema(data['Close'], 676)

# 生成交易信号
data['long_short'] = 0
data['long_short_color'] = 'silver'
data.loc[(data['EMA_12'] > data['EMA_144']) & (data['EMA_144'] > data['EMA_169']) & (data['EMA_169'] > data['EMA_576']) & (data['EMA_576'] > data['EMA_676']), 'long_short'] = 1
data.loc[(data['EMA_12'] < data['EMA_144']) & (data['EMA_144'] < data['EMA_169']) & (data['EMA_169'] < data['EMA_576']) & (data['EMA_576'] < data['EMA_676']), 'long_short'] = 2
data.loc[data['long_short'] == 1, 'long_short_color'] = 'green'
data.loc[data['long_short'] == 2, 'long_short_color'] = 'red'

data['state'] = 0
data['long_signal'] = False
data['short_signal'] = False

for i in range(1, len(data)):
    if data['long_short'].iloc[i] == 0:
        data.at[data.index[i], 'state'] = 0
    elif data['long_short'].iloc[i] == 1:
        if data['state'].iloc[i-1] == 0:
            if data['Low'].iloc[i] <= data['EMA_144'].iloc[i] and data['Close'].iloc[i] >= data['EMA_12'].iloc[i]:
                data.at[data.index[i], 'long_signal'] = True
                data.at[data.index[i], 'state'] = 0
            elif data['Low'].iloc[i] <= data['EMA_144'].iloc[i]:
                data.at[data.index[i], 'state'] = 1
            else:
                data.at[data.index[i], 'state'] = 0
        elif data['state'].iloc[i-1] == 1:
            if data['Close'].iloc[i] >= data['EMA_12'].iloc[i]:
                data.at[data.index[i], 'long_signal'] = True
                data.at[data.index[i], 'state'] = 0
            elif data['EMA_12'].iloc[i] <= data['EMA_144'].iloc[i]:
                data.at[data.index[i], 'state'] = 0
    elif data['long_short'].iloc[i] == 2:
        if data['state'].iloc[i-1] == 0:
            if data['High'].iloc[i] >= data['EMA_144'].iloc[i] and data['Close'].iloc[i] <= data['EMA_12'].iloc[i]:
                data.at[data.index[i], 'short_signal'] = True
                data.at[data.index[i], 'state'] = 0
            elif data['High'].iloc[i] >= data['EMA_144'].iloc[i]:
                data.at[data.index[i], 'state'] = 1
            else:
                data.at[data.index[i], 'state'] = 0
        elif data['state'].iloc[i-1] == 1:
            if data['Close'].iloc[i] <= data['EMA_12'].iloc[i]:
                data.at[data.index[i], 'short_signal'] = True
                data.at[data.index[i], 'state'] = 0
            elif data['EMA_12'].iloc[i] >= data['EMA_144'].iloc[i]:
                data.at[data.index[i], 'state'] = 0

# 绘制图表
plt.figure(figsize=(15, 10))

# 绘制价格和通道
plt.plot(data.index, data['Close'], label='收盘价')
plt.plot(data.index, data['EMA_12'], label='EMA 12', color='orange')
plt.plot(data.index, data['EMA_144'], label='EMA 144', color='#fff176')
plt.plot(data.index, data['EMA_169'], label='EMA 169', color='#ffa726')
plt.plot(data.index, data['EMA_576'], label='EMA 576', color='#26c6da')
plt.plot(data.index, data['EMA_676'], label='EMA 676', color='#42a5f5')

# 绘制交易信号
plt.plot(data[data['long_signal']].index, data['Close'][data['long_signal']], '^', markersize=10, color='g', label='多头信号')
plt.plot(data[data['short_signal']].index, data['Close'][data['short_signal']], 'v', markersize=10, color='r', label='空头信号')

plt.title('维加斯隧道策略')
plt.legend()
plt.show()