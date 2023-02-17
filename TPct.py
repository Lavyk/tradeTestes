# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# flake8: noqa: F401
# isort: skip_file
# --- Do not remove these libs ---
import numpy as np  # noqa
import pandas as pd  # noqa
from pandas import DataFrame
from typing import Optional, Union
from freqtrade.persistence import Trade

from freqtrade.strategy import (BooleanParameter, CategoricalParameter, DecimalParameter,
                                IStrategy, IntParameter)

# --------------------------------
# Add your lib to import here
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib


# This class is a sample. Feel free to customize it.
class TPct(IStrategy):
    """
    This is a sample strategy to inspire you.
    More information in https://www.freqtrade.io/en/latest/strategy-customization/

    You can:
        :return: a Dataframe with all mandatory indicators for the strategies
    - Rename the class name (Do not forget to update class_name)
    - Add any methods you want to build your strategy
    - Add any lib you need to build your strategy

    You must keep:
    - the lib in the section "Do not remove these libs"
    - the methods: populate_indicators, populate_entry_trend, populate_exit_trend
    You should keep:
    - timeframe, minimal_roi, stoploss, trailing_*
    """

    INTERFACE_VERSION = 3

    # Can this strategy go short?
    can_short: bool = False

    # minimal_roi = {
    #     "2880": 0.01,
    #     "1440": 0.02,
    #     "0": 0.03
    # }

    minimal_roi = {
        "0": 0.003
    }

    stoploss = -0.05

    trailing_stop = False
    # trailing_only_offset_is_reached = False
    # trailing_stop_positive = 0.01
    # trailing_stop_positive_offset = 0.0  # Disabled / not configured

    timeframe = '1m'

    # Run "populate_indicators()" only for new candle.
    # process_only_new_candles = True

    # These values can be overridden in the config.
    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False

    # Hyperoptable parameters
    # buy_rsi = IntParameter(low=1, high=50, default=30, space='buy', optimize=True, load=True)
    # sell_rsi = IntParameter(low=50, high=100, default=70, space='sell', optimize=True, load=True)
    # short_rsi = IntParameter(low=51, high=100, default=70, space='sell', optimize=True, load=True)
    # exit_short_rsi = IntParameter(low=1, high=50, default=30, space='buy', optimize=True, load=True)

    # Number of candles the strategy requires before producing valid signals
    startup_candle_count: int = 30

    # Optional order type mapping.
    order_types = {
        'entry': 'market',
        'exit': 'market',
        'stoploss': 'market',
        'stoploss_on_exchange': False
    }

    plot_config = {
        'main_plot': {
            'tema': {},
            'sar': {'color': 'white'},
        }
    }

    # def informative_pairs(self):
    #     pairs = self.dp.current_whitelist()
    #     informative_pairs = [(pair, '5m') for pair in pairs]
    #     return informative_pairs

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Adds several different TA indicators to the given DataFrame

        Performance Note: For the best performance be frugal on the number of indicators
        you are using. Let uncomment only the indicator you are using in your strategies
        or your hyperopt configuration, otherwise you will waste your memory and CPU usage.
        :param dataframe: Dataframe with data from the exchange
        :param metadata: Additional information, like the currently traded pair
        :return: a Dataframe with all mandatory indicators for the strategies
        """

        # Momentum Indicators
        # ------------------------------------

        dataframe["delta"] = 100 - ((dataframe['close'] / (((dataframe['high'] - dataframe['low'])/2) + dataframe['low'])) * 100)
        if('venda_alvo' not in dataframe.columns):
            dataframe['venda_alvo'] = 0.0
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        dataframe.loc[
            (
                (dataframe['venda_alvo'] == 0.0) &
                (dataframe['delta'] > 0) &
                (dataframe['volume'] > 0)  # Make sure Volume is not 0
            ),
            ['enter_long', 'venda_alvo']] = (1, np.sum([dataframe['close'], np.multiply(dataframe['close'], 0.01)]))
        
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the exit signal for the given dataframe
        :param dataframe: DataFrame
        :param metadata: Additional information, like the currently traded pair
        :return: DataFrame with exit columns populated
        """

        # print(dataframe['venda_alvo'])  

        dataframe.loc[
            (
                (dataframe['venda_alvo'] != 0.0) &
                (dataframe['close'] > dataframe['venda_alvo']) &
                (dataframe['volume'] > 0)  # Make sure Volume is not 0
            ),
            ['exit_long', 'venda_alvo']] = (1, 0.0)

        return dataframe

# def custom_exit(self, pair: str, trade: 'Trade', current_time: 'datetime', current_rate: float,
#                     current_profit: float, **kwargs):
#         # Between 2% and 10%, sell if EMA-long above EMA-short
#         if current_profit > 0.005:
#             return 'sell'

#         # Sell any positions at a loss if they are held for more than one day.
#         if current_profit < 0.0 and (current_time - trade.open_date_utc).days >= 1:
#             return 'sell'

#         return False