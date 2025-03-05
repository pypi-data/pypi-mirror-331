from backtrader_contrib.framework.lucid.utils.allocator_base import LucidAllocatorBase


class RotationModel(LucidAllocatorBase):
    """
    """
    params = LucidAllocatorBase.params + (
        ('lookback_window', 252),  # 12m
        ('assets', ["SPY", "TLT"]),
        ('offensive_trade', False),
        ('cash_proxy', "BIL"),  # US T-Bills as cash proxy
        ('canary', "TIP"),  # Canary asset
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.offensive_symbols = {
            'SPY': "SSO",
            'IWM': "UWM",
            'QQQ': "QLD",
            'VNQ': 'URE',
            'TLT': 'UBT',
            'IEF': 'UST'
        }

    def set_lookback_window(self):
        """ Ensure we have enough historical data for 1, 3, 6, and 12-month returns """
        return self.p.lookback_window

    def calculate_momentum(self, df, months=3):

        # Ensure DataFrame is sorted by date (ascending order)
        df = df.sort_index()
        # Compute momentum returns
        returns = (df.iloc[-1] - df.iloc[-months*21]) / df.iloc[-months*21]
        return returns

    def switch_to_offensive(self, weights):
        """
        the smart leverage approach incorporates a clever separation of signals and trades. As proposed by Matthias
        Koch, a quant from Germany, non-leveraged asset universes are used for signaling momentum based position
        sizing while universes that hold a limited number of matching leveraged funds are used for actual trading.

        When the stock market is in an uptrend - positive 13612W momentum for all canary assets -
        favorable conditions for leveraged stock positions are assumed targeting positive streaks in performance.
        When the stock market is in a downtrend - negative 13612W momentum for one or more of the canary assets -
        a rise in volatility is expected and a (relatively) safe Treasury bond position is acquired to avoid the
        constant leverage trap for stocks.

        Parameters:
        weights (dict): A dictionary containing asset symbols as keys and their weights as values.

        Returns:
        dict: A new dictionary with offensive symbols replaced.
        """
        offensive_weights = {}

        for symbol, weight in weights.items():
            # If the symbol exists in offensive_symbols, replace it with its offensive counterpart
            if symbol in self.offensive_symbols:
                offensive_weights[self.offensive_symbols[symbol]] = weight
            else:
                offensive_weights[symbol] = weight

        return offensive_weights

    def assign_equal_weight(self, today_date):

        etf_df = self.lucid_taa.adj_window.get_adjusted_window(today_date=today_date)

        # Calculate the momentum of each asset in the (risky) offensive, defensive (BIL/IEF) and canary (TIP)
        # universe, where momentum is the average total return over the past 1, 3, 6, and 12 months.
        asset_momentum = self.calculate_momentum(etf_df.get(self.p.assets), months=3)
        canary_momentum = self.calculate_momentum(etf_df.get(self.p.canary), months=6)
        cash_momentum = self.calculate_momentum(etf_df.get(self.p.cash_proxy), months=3)

        sma12 = etf_df[-252:].mean()
        sma6 = etf_df[-6*21:].mean()

        # allocate 1/TopX (equally weighted)
        eq_weight = 1 / float(self.p.nb_asset_in_portfolio)

        # select the best TopX half of the risky assets
        top_assets = asset_momentum.nlargest(self.p.nb_asset_in_portfolio).index.tolist()
        weights = {}

        if canary_momentum[0] > 0 or etf_df.get("SPY")[-1] > sma6.get("SPY"):
            for asset in top_assets:
                weights[asset] = eq_weight  # Assign 25% if positive momentum

            if self.p.offensive_trade:
                weights = self.switch_to_offensive(weights)

        else:
            # Defensive mode: Select only the best defensive ‘cash’ asset (BIL or IEF) when TIP is bad
            defensive_asset = cash_momentum.nlargest(1).index.tolist()[0]
            weights = {defensive_asset: 1.0}

        return weights
