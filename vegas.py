import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

class VegasTunnelStrategy:
    def __init__(self, symbol="AAPL", start_date="2022-01-01", end_date="2024-03-01"):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.data = None
        self.atr_period = 20
        self.ema_period = 20
        self.atr_multiplier = 2.0
        
    def download_data(self):
        try:
            self.data = yf.download(self.symbol, start=self.start_date, end=self.end_date)
            if self.data.empty:
                raise ValueError("下载的数据为空")
            return True
        except Exception as e:
            print(f"数据下载失败: {e}")
            return False
            
    def calculate_indicators(self):
        # 计算ATR
        high_low = self.data['High'] - self.data['Low']
        high_close = np.abs(self.data['High'] - self.data['Close'].shift())
        low_close = np.abs(self.data['Low'] - self.data['Close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        self.data['ATR'] = true_range.rolling(self.atr_period).mean()
        
        # 计算EMA
        self.data['EMA'] = self.data['Close'].ewm(span=self.ema_period, adjust=False).mean()
        
        # 计算通道
        self.data['Upper_Band'] = self.data['EMA'] + self.data['ATR'] * self.atr_multiplier
        self.data['Lower_Band'] = self.data['EMA'] - self.data['ATR'] * self.atr_multiplier
        
    def generate_signals(self):
        self.data['Position'] = 0
        # 生成交易信号
        self.data.loc[self.data['Close'] > self.data['Upper_Band'], 'Position'] = 1
        self.data.loc[self.data['Close'] < self.data['Lower_Band'], 'Position'] = -1
        
    def calculate_returns(self):
        self.data['Returns'] = self.data['Close'].pct_change()
        self.data['Strategy_Returns'] = self.data['Position'].shift(1) * self.data['Returns']
        self.data['Cumulative_Returns'] = (1 + self.data['Strategy_Returns']).cumprod()
        
    def plot_strategy(self):
        plt.figure(figsize=(15, 10))
        
        # 绘制价格和通道
        plt.subplot(2, 1, 1)
        plt.plot(self.data.index, self.data['Close'], label='收盘价')
        plt.plot(self.data.index, self.data['EMA'], label='EMA', color='orange')
        plt.plot(self.data.index, self.data['Upper_Band'], label='上轨', color='g')
        plt.plot(self.data.index, self.data['Lower_Band'], label='下轨', color='r')
        plt.title('维加斯隧道策略')
        plt.legend()
        
        # 绘制累计收益
        plt.subplot(2, 1, 2)
        plt.plot(self.data.index, self.data['Cumulative_Returns'], label='策略收益')
        plt.plot(self.data.index, (1 + self.data['Returns']).cumprod(), label='买入持有收益')
        plt.title('累计收益对比')
        plt.legend()
        
        plt.tight_layout()
        plt.show()
        
    def run_strategy(self):
        if not self.download_data():
            return
            
        self.calculate_indicators()
        self.generate_signals()
        self.calculate_returns()
        
        # 计算策略表现
        total_return = self.data['Cumulative_Returns'].iloc[-1] - 1
        annual_return = (total_return + 1) ** (252 / len(self.data)) - 1
        max_drawdown = (self.data['Cumulative_Returns'] / self.data['Cumulative_Returns'].cummax() - 1).min()
        
        print(f"\n策略表现：")
        print(f"总收益率: {total_return:.2%}")
        print(f"年化收益率: {annual_return:.2%}")
        print(f"最大回撤: {max_drawdown:.2%}")
        
        self.plot_strategy()

# 运行策略
strategy = VegasTunnelStrategy()
strategy.run_strategy()