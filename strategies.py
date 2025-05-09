# strategies.py
# 此模块用于统一存放书写的策略类，数据来源为mini QMT
# 初始化策略的时候需要实例化broker来获取数据：self.mbroker = my_broker(use_real_trading=self.p.use_real_trading)
# 需要输入参数来判断时候需要发送委托：
# params = (
#         ('use_real_trading', False),  # 默认参数
#     )
# 如果需要发送委托需要自行插入broker的buy()方法
from tabulate import tabulate

import backtrader as bt
from qmtbt import QMTStore
from datetime import datetime
from xtquant import xtdata, xtconstant
import math
import backtrader as bt
from xtquant.xttrader import XtQuantTrader, XtQuantTraderCallback
from xtquant.xttype import StockAccount
import backtrader as bt
class MyXtQuantTraderCallback(XtQuantTraderCallback):
    def on_disconnected(self):
        print("[连接状态] 与交易服务器连接断开")

    def on_stock_order(self, order):
        print("\n[委托单回调] 订单状态更新")
        print(f"证券代码: {order.stock_code}")
        print(f"订单状态: {order.order_status}")  # 需根据券商文档映射状态码含义
        print(f"系统订单号: {order.order_sysid}")

    def on_stock_asset(self, asset):
        print("\n[账户资产] 资金变动通知")
        print(f"账户ID: {asset.account_id}")
        print(f"可用资金: {asset.cash}")
        print(f"总资产估值: {asset.total_asset}")

    def on_stock_trade(self, trade):
        print("\n[成交记录] 交易已达成")
        print(f"账户ID: {trade.account_id}")
        print(f"证券代码: {trade.stock_code}")
        print(f"关联订单号: {trade.order_id}")

    def on_stock_position(self, position):
        print("\n[持仓变动] 头寸更新")
        print(f"证券代码: {position.stock_code}")
        print(f"当前持仓量: {position.volume}")

    def on_order_error(self, order_error):
        print("\n[委托失败] 订单提交错误")
        print(f"错误订单号: {order_error.order_id}")
        print(f"错误代码: {order_error.error_id}")
        print(f"错误详情: {order_error.error_msg}")  # 建议根据error_id映射具体原因

    def on_cancel_error(self, cancel_error):
        print("\n[撤单失败] 取消订单错误")
        print(f"目标订单号: {cancel_error.order_id}")
        print(f"错误代码: {cancel_error.error_id}")
        print(f"错误信息: {cancel_error.error_msg}")

    def on_order_stock_async_response(self, response):
        print("\n[异步响应] 委托请求已受理")
        print(f"账户ID: {response.account_id}")
        print(f"订单号: {response.order_id}")
        print(f"请求序列号: {response.seq}")

    def on_account_status(self, status):
        print("\n[账户状态] 登录/连接状态变化")
        print(f"账户ID: {status.account_id}")
        print(f"账户类型: {status.account_type}")  # 如普通户/信用户
        print(f"当前状态: {status.status}")
        # 需映射状态码（如已连接/断开）



class my_broker:
    def __init__(self, use_real_trading=False):
        self.path = r'E:\software\QMT\userdata_mini'
        self.session_id = 123456
        self.xt_trader = XtQuantTrader(self.path, self.session_id)
        callback = MyXtQuantTraderCallback()
        self.acc = StockAccount('39131771')
        self.xt_trader.register_callback(callback)
        self.use_real_trading = use_real_trading  # 新增标志位判断是否实盘

        if use_real_trading:#如果实盘才连接
            self.xt_trader.start()
            connect_result = self.xt_trader.connect()
            if connect_result != 0:
                import sys
                sys.exit('链接失败，程序即将退出 %d' % connect_result)
            subscribe_result = self.xt_trader.subscribe(self.acc)
            if subscribe_result != 0:
                print('账号订阅失败 %d' % subscribe_result)

    def buy(self, stock_code, price, quantity):
        if self.use_real_trading:
            fix_result_order_id = self.xt_trader.order_stock(self.acc, stock_code, xtconstant.STOCK_BUY, quantity, xtconstant.FIX_PRICE, price)
            print(fix_result_order_id)
        else:
            print("模拟买入，股票代码: %s, 价格: %.2f, 数量: %d" % (stock_code, price, quantity))

    def sell(self, stock_code, price, quantity):
        if self.use_real_trading:
            fix_result_order_id = self.xt_trader.order_stock(self.acc, stock_code, xtconstant.STOCK_SELL, quantity, xtconstant.FIX_PRICE, price)
            print(fix_result_order_id)
        else:
            print("模拟卖出，股票代码: %s, 价格: %.2f, 数量: %d" % (stock_code, price, quantity))

    def cancel_order(self, order_id):
        if self.use_real_trading:
            self.xt_trader.cancel_order_stock(self.acc, order_id)

    def query_order(self):
        """查询委托订单（支持真实/模拟交易）"""

        orders = self.xt_trader.query_stock_orders(self.acc, False)
        order_list = []
        orders = self.xt_trader.query_stock_orders(self.acc, False)

        # 检查列表是否为空
        # if orders:
        #     # 获取第一个订单对象以查看其属性
        #     first_order = orders[0]
        #
        #     # 使用 dir() 函数查看第一个订单对象的所有属性和方法
        #     attributes = dir(first_order)
        #
        #     # 过滤掉特殊方法和属性（以 '__' 开头和结尾的）
        #     attributes = [attr for attr in attributes if not attr.startswith('__') and not attr.endswith('__')]
        #
        #     # 打印出所有属性
        #     print("订单对象的属性和方法:", attributes)
        # else:
        #     print("没有找到任何订单。")

        for o in orders:

            order_time = datetime.fromtimestamp(o.order_time).strftime('%Y-%m-%d %H:%M:%S')
            order_list.append({
                "委托时间": order_time,
                "证券代码": o.stock_code,
                "方向":o.order_type,
                "委托价": o.price,
                "状态":o.order_status,
                "委托ID": o.order_id,
                "数量":o.order_volume
            })

        print("\n当日委托明细：")
        print(tabulate([list(o.values()) for o in order_list],
                       headers=order_list[0].keys(),
                       tablefmt="grid"))
        return order_list


    def query_asset(self):
        asset = self.xt_trader.query_stock_asset(self.acc)
        asset_data = {
            "总资产": round(asset.total_asset, 2),
            "持仓市值": round(asset.market_value, 2),
        }
        print("\n账户资产概览：")
        print(tabulate([list(asset_data.values())],
                       headers=asset_data.keys(),
                       floatfmt=".2f",
                       tablefmt="grid"))
        return asset_data

    def query_trades(self):
        """查询成交记录（支持真实/模拟交易）"""
        print("\n====== 成脚明细 ======")
        try:
            trades = self.xt_trader.query_stock_trades(self.acc)
            if not trades:
                print('今日没有成交')
            trade_list = []
            for t in trades:
                trade_list.append({
                    "成交时间": datetime.datetime.fromtimestamp(t.trade_time / 1000).strftime('%Y-%m-%d %H:%M:%S'),
                    "证券代码": t.stock_code,
                    "方向": self._format_direction(t.order_type),
                    "成交价": t.price,
                    "数量": t.volume,
                    "成交ID": t.trade_id
                })


        except Exception as e:
            print(f"成交查询异常: {str(e)}")
            return []

    def query_stock_positions(self):
        positions = self.xt_trader.query_stock_positions(self.acc)
        print("\n====== 持仓明细 ======")

        for pos in positions:
            print(f"股票: {pos.stock_code} | "
                  f"数量: {pos.volume} | "
                  f"可用: {pos.can_use_volume} | "
                  f"成本: {pos.open_price:.2f}")
        return positions


class TestStrategy(bt.Strategy):
    params = (
        ('use_real_trading', False),
        ('any', 50),
    )

    def log(self, txt, dt=None, data=None):
        dt = dt or data.datetime.date(0)
        print(f'{dt.isoformat()}, {data._name}, {txt}')

    def __init__(self):
        # 用字典跟踪每个数据的订单和状态
        self.orders = {}
        self.bar_executed = {}
        for d in self.datas:
            self.orders[d] = None  # 跟踪每个数据的订单
            self.bar_executed[d] = 0  # 跟踪每个数据的买入时间

        self.mbroker = my_broker(use_real_trading=self.p.use_real_trading)

    def notify_order(self, order):
        # 获取对应的数据对象
        d = order.data
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED {order.executed.price:.2f}', data=d)
            elif order.issell():
                self.log(f'SELL EXECUTED {order.executed.price:.2f}', data=d)
            self.bar_executed[d] = len(self)  # 记录当前数据的买入时间

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected', data=d)

        # 重置该数据的订单状态
        self.orders[d] = None

    def next(self):
        for d in self.datas:
            stock_code = d._name
            close_price = d.close[0]
            position = self.getposition(d)

            # 如果该数据有未完成订单则跳过
            if self.orders[d]:
                continue

            # 空仓条件（针对当前数据）
            if not position:
                if close_price < d.close[-1] and d.close[-1] < d.close[-2]:
                    self.mbroker.buy(
                        stock_code=stock_code,
                        price=close_price,
                        quantity=200
                    )
                    self.log(f'BUY CREATE {close_price:.2f}', data=d)
                    self.orders[d] = self.buy(data=d)  # 记录该数据的订单

            # 持仓条件（针对当前数据）
            else:
                if (len(self) >= (self.bar_executed[d] + 5)):
                    self.mbroker.sell(
                        stock_code=stock_code,
                        price=close_price,
                        quantity=200
                    )
                    self.log(f'SELL CREATE {close_price:.2f}', data=d)
                    self.orders[d] = self.sell(data=d)

class AnotherStrategy(bt.Strategy):
    params = (('period1', 10),
              ('period2', 30),
              ('period3', 30),
              ('use_real_trading', False),
              )
    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None
        self.mbroker = my_broker(use_real_trading=self.p.use_real_trading)  # 默认不使用实盘

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, %.2f' % order.executed.price)
            elif order.issell():
                self.log('SELL EXECUTED, %.2f' % order.executed.price)

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def next(self):
        data = self.datas[0]
        stock_code = data._name
        self.log('Close, %.2f' % self.dataclose[0])

        if self.order:
            return

        if not self.position:
            if self.dataclose[0] > self.dataclose[-1]:
                if self.dataclose[-1] > self.dataclose[-2]:
                    # 模拟下单
                    self.mbroker.buy(stock_code=stock_code, price=self.dataclose[0], quantity=200)
                    self.log('BUY CREATE, %.2f' % self.dataclose[0])
                    self.order = self.buy()

        else:
            if len(self) >= (self.bar_executed + 5):
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                self.order = self.sell()
class SmaCross(bt.SignalStrategy):
    params = (('period1', 10),
              ('period2', 30),
              ('use_real_trading', False),
              )

    def __init__(self):
        sma1, sma2 = bt.ind.SMA(period=self.p.period1), bt.ind.SMA(period=self.p.period2)
        crossover = bt.ind.CrossOver(sma1, sma2)
        self.signal_add(bt.SIGNAL_LONG, crossover)


class MultiSMACrossStrategy(bt.Strategy):
    params = (
        ('fast_length', 5),
        ('slow_length', 25)
    )

    def __init__(self):
        self.crossovers = []

        for d in self.datas:
            ma_fast = bt.ind.SMA(d, period=self.params.fast_length)
            ma_slow = bt.ind.SMA(d, period=self.params.slow_length)

            self.crossovers.append(bt.ind.CrossOver(ma_fast, ma_slow))

    def next(self):
        for i, d in enumerate(self.datas):
            if not self.getposition(d).size:
                if self.crossovers[i] > 0:
                    self.buy(data=d, size=100)
            elif self.crossovers[i] < 0:
                if self.getposition(d).size > 0:
                    self.close(data=d)

if __name__ == '__main__':
    broker=my_broker(use_real_trading=True)
    broker.query_stock_positions()
    broker.query_order()
    broker.query_asset()
    broker.query_trades()

