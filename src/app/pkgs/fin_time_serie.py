import yfinance as yf
import numpy as np
from sklearn.linear_model import LinearRegression
import pandas as pd
import matplotlib.pyplot as plt
import pprint
from typing import Dict, Any, List

pp = pprint.PrettyPrinter(indent=4)

class FinTimeSerie:

    def __init__(self, symbol: str, 
                 start_period: str, download: bool=True) -> None:

        self.start_period = start_period
        self.ticker = symbol.upper()
        self.pct_change = None

        if download:
            self.adj_close = yf.download(symbol, start_period)['Adj Close']
            self.adj_close = self.adj_close.fillna(0)
            self.close_props()
            self.returns_props()
        else:
            self.adj_close = None

    def set_adj_close(self, adj_close: pd.Series):
        self.adj_close = adj_close
        self.close_props()
        self.returns_props()


    def close_props(self) -> None:
        try:
            self.drawdown = self.adj_close - self.adj_close.cummax()
            self.pct_change = self.adj_close.pct_change()
            self.pct_change.fillna(0, inplace=True)
        except Exception:
            raise Exception

    def returns_props(self) -> None:
        self.returns_std_neg = self.pct_change[self.pct_change<0].std()
        self.returns_std_pos = self.pct_change[self.pct_change>0].std()
        self.returns_std = np.array(self.pct_change).std()

    def get_props(self) -> Dict[str, Any]:
        return {
                'ticker' : self.ticker,
                'prices': {
                    'std': np.array(self.adj_close).std(),
                    'min': np.array(self.adj_close).min(),
                    'max': np.array(self.adj_close).max(),
                    'mean': np.array(self.adj_close).mean(),
                    'return': self.period_return(),
                    'first': self.first_close(),
                    'last': self.last_close(),
                    'max_draw_pct': np.abs(self.drawdown.min()) / self.adj_close.max(),
                    'avg_draw_down': np.abs(self.drawdown.mean()),
                    'std_draw_down': np.abs(self.drawdown.std())
                },
                'returns': {
                    'std': self.returns_std,
                    'std_neg': self.returns_std_neg,
                    'std_pos': self.returns_std_pos,
                    'min': np.array(self.pct_change).min(),
                    'max': np.array(self.pct_change).max(),
                    'mean': np.array(self.pct_change).mean(),
                    'sortino': self.sortino(),
                    'sharpe': self.sharpe(),
                    'calmar': self.adj_close.max() * self.period_return() / np.abs(self.drawdown.min())
                    }
                }

    def beta(self, ticker: "FinTimeSerie") -> float:

        x = np.array(ticker.pct_change).reshape((-1,1))
        y = np.array(self.pct_change)
        model = LinearRegression().fit(x, y)
        beta = model.coef_[0]

        return beta
    
    def last_close(self) -> float:
        return self.adj_close.iloc[-1]

    def first_close(self):
        return self.adj_close.iloc[0]

    def period_return(self) -> float:
        r = (self.last_close() - self.first_close()) / self.first_close()
        return r

    def sharpe(self) -> float:
        return self.period_return() / self.returns_std

    def sortino(self) -> float:
        return self.period_return() / self.returns_std_neg

def example_beta() -> None:
    start_period = '2021-04-06'
    spy = FinTimeSerie('SPY', start_period)
    aapl = FinTimeSerie('AAPL', start_period)
    print(aapl.beta(spy))

    pp.pprint(spy.get_props())


if __name__ == "__main__":
    example_beta()
