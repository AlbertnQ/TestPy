import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# 获取股票数据
symbol = "AAPL"
start_date = "2022-01-01"
end_date = "2024-12-03"

try:
    data = yf.download(symbol, start=start_date, end=end_date)
    if data.empty:
        raise ValueError("下载的数据为空，请检查股票代码和日期范围。")
except Exception as e:
    print(f"数据下载失败: {e}")
    exit()

# 计算简单移动平均线
data['SMA_50'] = data['Close'].rolling(window=50).mean()
data['SMA_200'] = data['Close'].rolling(window=200).mean()

data['Signal'] = 0

# 计算交叉信号
data.loc[data['SMA_50'] > data['SMA_200'], 'Signal'] = 1
data.loc[data['SMA_50'] < data['SMA_200'], 'Signal'] = -1

# 计算每日收益率
data['Daily_Return'] = data['Close'].pct_change()

# 计算策略信号的收益率（shift(1) 是为了避免未来数据的偏差）
data['Strategy_Return'] = data['Signal'].shift(1) * data['Daily_Return']

# 计算累计收益
data['Cumulative_Return'] = (1 + data['Strategy_Return']).cumprod()

# 检查数据是否足够长以进行计算
if len(data) < 252:
    print("数据长度不足，无法计算年度收益率。")
    exit()

# 输出策略表现
strategy_performance = {
    'Total Return': data['Cumulative_Return'].iloc[-1] - 1,
    'Annualized Return': (data['Cumulative_Return'].iloc[-1] ** (252 / len(data))) - 1,
    'Max Drawdown': (data['Cumulative_Return'] / data['Cumulative_Return'].cummax() - 1).min(),
}

print("策略表现:")
for key, value in strategy_performance.items():
    print(f"{key}: {value:.4f}")

# 绘制累计收益曲线
plt.figure(figsize=(10, 6))
plt.plot(data['Cumulative_Return'], label='Strategy Cumulative Return', color='b')
plt.plot(data['Close'] / data['Close'].iloc[0], label='Stock Cumulative Return', color='g')
plt.title("Cumulative Return of Strategy vs. Stock")
plt.xlabel("Date")
plt.ylabel("Cumulative Return")
plt.legend()
plt.show()

#finish