# 此方法实现了为每一只股票单独选择最优参数进行回测


from sko.GA import GA

import backtrader as bt
from qmtbt import QMTStore
from datetime import datetime
from xtquant import xtdata, xtconstant
import math
import backtrader as bt
from strategies import TestStrategy, AnotherStrategy ,my_broker
from xtquant.xttrader import XtQuantTrader, XtQuantTraderCallback
from xtquant.xttype import StockAccount
import optuna
from strategies import *
def finetune(Strategy, method='Sko', stocks=['000001.SZ'],
             timeframe=bt.TimeFrame.Days, fromdate=datetime(2025, 1, 1),
             todate=datetime(2025, 4, 1), count=1):
    """为所有股票优化统一参数"""
    store = QMTStore()
    optimized_params = {}

    # 获取策略可优化参数列表
    default_params = {
        name: value for name, value in Strategy.params._getitems()
        if not name.startswith('_') and name not in ['signals', 'use_real_trading']
    }
    param_names = list(default_params.keys())

    # 加载所有股票数据
    datas = []
    for stock in stocks:
        data = store.getdata(dataname=stock, timeframe=timeframe,
                             fromdate=fromdate, todate=todate, live=False)
        datas.append(data)
    if method == 'Sko':
        n_dim = len(param_names)
        lb = [1] * n_dim
        ub = [50] * n_dim
        history=[]
        def backtest(p):
            cerebro = bt.Cerebro()
            for data in datas:

                cerebro.adddata(data)
            param_dict = {name: int(round(value)) for name, value in zip(param_names, p)}
            # 重置 cerebro 以清除之前的策略结果
            # cerebro.reset()
            cerebro.addstrategy(Strategy, **param_dict)
            cerebro.broker.setcash(1000000)
            cerebro.broker.setcommission(0.00025)
            results = cerebro.run()
            # 计算所有股票的平均收益
            avg_value = sum([strat.broker.getvalue() for strat in results]) / len(results)
            stock_returns = {
                stock: strat.broker.getvalue()
                for stock, strat in zip(stocks, results)
            }
            history.append({
                'iteration': len(history) + 1,
                'params': param_dict,
                'stock_returns': stock_returns,  # 新增每只股票收益
                'avg_return': avg_value
            })
            # 实时打印每次迭代结果
            print(f"\nIteration {len(history)}")
            print(f"Params: {param_dict}")
            for stock, ret in stock_returns.items():
                print(f"  {stock}: {ret:.2f}")
            print(f"Avg Return: {avg_value:.2f}")
            return -avg_value

        ga = GA(func=backtest, n_dim=n_dim, size_pop=10, max_iter=count, prob_mut=0.001, lb=lb, ub=ub, precision=1e-7)
        best_x, best_y = ga.run()
        optimized_params = {k: int(v) for k, v in zip(param_names, best_x)}
        print("\n===== 参数优化历史记录 =====")
        for i, record in enumerate(history):
            print(f"Iter {i + 1}: Params={record['params']} => Return={record['return']:.2f}")

        # 最佳结果
        print(f"\n最佳参数: {optimized_params},{best_y}")


    elif method == 'Optuna':
        history = []
        def objective(trial):
            cerebro = bt.Cerebro()
            for data in datas:

                cerebro.adddata(data)
            params = {name: trial.suggest_int(name, 1, 50)
                      for name in param_names}
            # cerebro = bt.Cerebro()
            # for data in datas:
            #     cerebro.adddata(data)
            # 重置 cerebro 以清除之前的策略结果
            # cerebro.reset()
            cerebro.addstrategy(Strategy, **params)
            cerebro.broker.setcash(1000000)
            cerebro.broker.setcommission(0.00025)
            results = cerebro.run()
            # 计算所有股票的平均收益
            avg_value = sum([strat.broker.getvalue() for strat in results]) / len(results)
            history.append({
                'iteration': len(history) + 1,
                'params': params,
                'avg_return': avg_value
            })
            return avg_value

        study = optuna.create_study(direction='maximize')
        study.optimize(objective, n_trials=count)
        optimized_params = study.best_params

    print(f"\n优化完成，参数：{optimized_params}")
    for i,record in enumerate(history):
        print(record)
    return optimized_params



def back_test(selected_strategy,

              optimized_params,
              use_real_trading=False,
              live=False,
              stocks=['000001.SZ'],
              fromdate=datetime(2020, 1, 1),
              todate=datetime(2021, 4, 1),
              ):
    """多股票独立参数回测"""

    store = QMTStore()

    results={}

    for stock in stocks:
        cerebro = bt.Cerebro()
        # 加载数据
        data = store.getdata(
            dataname=stock,
            timeframe=bt.TimeFrame.Days,
            fromdate=datetime(2020, 1, 1),
            todate=datetime(2021, 4, 1),
            live=live
        )
        cerebro.adddata(data)

        # 添加带独立参数的策略
        cerebro.addstrategy(
            selected_strategy,
            **optimized_params[stock],
            use_real_trading=use_real_trading
        )

        # 资金管理
        cerebro.broker.setcash(1000000.0)
        cerebro.broker.setcommission(commission=0.001)

    # 运行回测
        cerebro.run()
        # cerebro.plot(style='candlestick', iplot=False)
        print(f"\n总资产: {cerebro.broker.getvalue():.2f}")
        results[stock] = cerebro.broker.getvalue()
    for stock, total_value in results.items():
        print(f"{stock} 总资产: {total_value:.2f}")

    return cerebro


if __name__ == '__main__':
    stra=TestStrategy

    code_list = xtdata.get_stock_list_in_sector('上证A股')

    print(code_list)

    # Sko 多只股票同时测试，得到多组参数
    optuna_params = finetune(
        stra,
        method='Optuna',
        # stocks=['600519.SH', '000001.SZ', '300750.SZ'],
        stocks=['600051.SH'],
        # stocks=code_list[:10],
        count=10
    )
    print(optuna_params)


    # Optuna 多只股票同时测试，得到多组参数
    # optuna_params = finetune(
    #     stra,
    #     method='Optuna',
    #     stocks=['600519.SH'],
    #     count=1
    # )
    # print(optuna_params)

    # back_test(
    #     selected_strategy=stra,
    #     stocks=['600519.SH', '000001.SZ', '300750.SZ'],
    #     optimized_params=optuna_params,
    #
    # )



    # 使用优化参数进行测试,可以传入count来控制迭代次数
    # back_test(
    #     selected_strategy=stra,
    #     optimized_params=optuna_params,
    #     use_real_trading=False,
    #     stocks=['600519.SH']  # 使用与优化时相同的标的
    # )

    # use_real_trading=True 则是真实发送订单
    # back_test(
    #     selected_strategy=stra,
    #     optimized_params=optuna_params,
    #     use_real_trading=True,
    #     stocks=['600519.SH']  # 使用与优化时相同的标的
    # )


# 实时交易，但不能多只股票同时
#     back_test(
#         selected_strategy=stra,
#         optimized_params=optuna_params,
#         use_real_trading=False,
#         stocks=['600519.SH'],  # 使用与优化时相同的标的
#         live=False
#     )

















