import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# 获取股票数据
symbol = "AAPL"
start_date = "2022-01-01"
end_date = "2024-12-05"

try:
    data = yf.download(symbol, start=start_date, end=end_date)
    if data.empty:
        raise ValueError("下载的数据为空，请检查股票代码和日期范围。")
except Exception as e:
    print(f"数据下载失败: {e}")
    exit()

# 简单的数据分析
print(data.describe())

# 绘制股价走势图
data['Close'].plot(figsize=(10, 6), label=symbol)
plt.title(f"{symbol} Stock Price")
plt.xlabel("Date")
plt.ylabel("Price")
plt.legend()
plt.show()


# 输出苹果股票2024年2月1日的股价
try:
    data_2024_02_01 = data.loc["2024-02-01"]
    print(data_2024_02_01['Close'])
except KeyError:
    print("2024年2月1日的数据不存在。")