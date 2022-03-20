from jqdata import *
import pandas as pd


# set initialize method
def initialize(context):
    # set baseline
    set_benchmark('000300.XSHG')
    # set order cost
    set_order_cost(OrderCost(open_tax=0, close_tax=0.001, open_commission=0.0003,
                             close_commission=0.0003, close_today_commission=0, min_commission=5), type='stock')
    # use real price
    set_option('use_real_price', True)
    # set_option('order_volume_ratio', 1)
    run_monthly(get_under_valued, 1, time='9:30', force=False)
    run_weekly(trade, 1, time='9:30', force=False)


# set monthly method
# get security codes, PE ratio, PB ratio, ROE and GPM data
# filter data based on conditions below:
#     PE<15
#     PB<2
#     ROE>0.5
#     GPM>0.5
def get_under_valued(context):
    query_undervalued = query(valuation.code,
                              valuation.pe_ratio,
                              valuation.pb_ratio,
                              indicator.roe,
                              indicator.gross_profit_margin,
                              ).filter(valuation.pe_ratio > 0,
                                       valuation.pe_ratio < 15,
                                       valuation.pb_ratio > 0,
                                       valuation.pb_ratio < 2,
                                       indicator.roe > 5,
                                       indicator.gross_profit_margin > 50)
    g.stock_df = get_fundamentals(query_undervalued)['code']


# set weekly method
def trade(context):
    # get stocks to buy
    stocks_to_buy = g.stock_df
    # get stocks to sell
    stocks_to_sell = set(context.portfolio.positions.keys()) - set(stocks_to_buy)
    # sell the stocks not on the target list
    for stock in stocks_to_sell:
        order_target(stock, 0)
    # rebalance
    if len(stocks_to_buy) == 0:
        return
    else:
        # get weights
        weights = [1.0 / len(stocks_to_buy), ] * len(stocks_to_buy)
        vals = [wts * context.portfolio.total_value for wts in weights]
        value_stocks = pd.Series(vals, index=stocks_to_buy)
        for stocks in stocks_to_buy:
            order_value(stocks, value_stocks[stocks])
