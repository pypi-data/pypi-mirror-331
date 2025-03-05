import pandas as pd
from arch import arch_model
from backtrader_contrib.framework.lucid.utils.allocator_base import LucidAllocatorBase


class SectorRotationGiordano(LucidAllocatorBase):
    """
    Antifragile Asset Allocation (AAA) Strategy

    The AAA strategy dynamically allocates assets to a portfolio based on a ranking system that integrates four key factors:
    - **Absolute Momentum (M)**: Measures the profitability of assets over a specific lookback period (default: 4 months).
    - **Volatility (V)**: Measures the risk of assets using a GARCH(1,1) model, which provides dynamic volatility estimates.
    - **Average Relative Correlation (C)**: Measures diversification by calculating the average correlation across the assets, ensuring the portfolio isn’t overly correlated.
    - **ATR Trend/Breakout System (T)**: Measures the directionality of price movements using Average True Range (ATR) bands, helping to identify breakout or breakdown events.

    **Portfolio Construction and Hedging**:
    - The strategy ranks assets based on a combined score, TRank, which is calculated by weighting the four factors above.
    - **Top 5 ETFs**: The strategy selects the top 5 ETFs by TRank score and allocates them proportionally.

    Parameters:
    -----------
    momentum_window : int
        Lookback period for calculating Absolute Momentum (default: 84 days, ~4 months).
    volatility_window : int
        Lookback period for calculating Volatility (default: 84 days).
    correlation_window : int
        Lookback period for calculating Average Relative Correlation (default: 84 days).
    atr_window : int
        Lookback period for calculating ATR (default: 42 days).
    high_period : int
        Lookback period for the highest close in ATR bands (default: 63 days).
    low_period : int
        Lookback period for the lowest close in ATR bands (default: 105 days).
    nb_asset_in_portfolio : int
        Number of top ETFs to include in the portfolio (default: 3).
    hedge_asset : str
        Asset to use as Cash (default: 'SHY').
    momentum_weight : float
        Weight for Absolute Momentum in TRank calculation (default: 0.4).
    volatility_weight : float
        Weight for Volatility in TRank calculation (default: 0.2).
    correlation_weight : float
        Weight for Correlation in TRank calculation (default: 0.2).
    atr_weight : float
        Weight for ATR Trend in TRank calculation (default: 0.2).
    """
    params = LucidAllocatorBase.params + (
        ('momentum_window', 84),
        ('volatility_window', 84),
        ('correlation_window', 84),
        ('atr_window', 42),
        ('high_period', 63),
        ('low_period', 105),
        ('hedge_asset', 'SHY'),
        ('momentum_weight', 1),
        ('volatility_weight', 1),
        ('correlation_weight', 1),
        ('atr_weight', 1),  # todo: OHLC
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def set_lookback_window(self):
        return max(self.p.momentum_window, self.p.volatility_window, self.p.correlation_window, self.p.atr_window,
                   self.p.high_period, self.p.low_period)

    def absolute_momentum(self, df):
        df_subset = df.iloc[-self.p.momentum_window:]
        momentum_values = (df_subset.iloc[-1] / df_subset.iloc[0] - 1) * 100
        return momentum_values.rank(ascending=False, method='min')

    def compute_garch_volatility(self, df):
        df_subset = df.iloc[-self.p.volatility_window:]
        returns = df_subset.pct_change().dropna()
        volatility_today = {}

        for asset in returns.columns:
            try:
                garch = arch_model(returns[asset], vol='Garch', p=1, q=1)
                res = garch.fit(disp='off')
                volatility_today[asset] = res.conditional_volatility.iloc[-1]
            except:
                volatility_today[asset] = None

        volatility_series = pd.Series(volatility_today)
        return volatility_series.rank(ascending=False, method='min')

    def compute_avg_correlation(self, df):
        df_subset = df.iloc[-self.p.correlation_window:]
        returns = df_subset.pct_change().dropna()
        corr_matrix = returns.corr()
        avg_corr_today = corr_matrix.mean().dropna()
        return avg_corr_today.rank(ascending=False, method='min')

    def compute_atr_trend(self, df):
        atr_trend_today = {}
        lookback_window = max(self.p.atr_window, self.p.low_period, self.p.high_period)
        df_subset = df.iloc[-lookback_window:]

        for asset in df.columns:
            try:
                true_range = df_subset[asset].rolling(self.p.atr_window).max() - df_subset[asset].rolling(
                    self.p.atr_window).min()
                atr = true_range.rolling(self.p.atr_window, min_periods=self.p.atr_window).mean()
                highest_close_63 = df_subset[asset].rolling(self.p.high_period, min_periods=self.p.high_period).max()
                upper_band = highest_close_63 + atr
                highest_low_105 = df_subset[asset].rolling(self.p.low_period, min_periods=self.p.low_period).max()
                lower_band = highest_low_105 - atr
                atr_trend_today[asset] = ((df_subset[asset].iloc[-1] > upper_band.iloc[-1]).astype(int) -
                                          (df_subset[asset].iloc[-1] < lower_band.iloc[-1]).astype(int))
            except:
                atr_trend_today[asset] = None

        return pd.Series(atr_trend_today)

    def compute_trank(self, df):
        momentum_df = self.absolute_momentum(df)
        volatility_df = self.compute_garch_volatility(df)
        correlation_df = self.compute_avg_correlation(df)
        atr_df = self.compute_atr_trend(df)

        trank = (
                self.p.momentum_weight * momentum_df +
                self.p.volatility_weight * volatility_df +
                self.p.correlation_weight * correlation_df -
                self.p.atr_weight * atr_df
        )

        return trank.rank(ascending=True, method='min')

    def assign_equal_weight(self, today_date):
        etf_df = self.lucid_taa.adj_window.get_adjusted_window(today_date=today_date)

        trank = self.compute_trank(etf_df)
        top_etfs = trank.nsmallest(self.p.nb_asset_in_portfolio).index.tolist()
        equal_weight = 1.0 / len(top_etfs)

        return {etf: equal_weight for etf in top_etfs}
