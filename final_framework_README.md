# finetune

```python
    stra=MultiSMACrossStrategy

    code_list = xtdata.get_stock_list_in_sector('上证A股')

    print(code_list)

    # Sko 多只股票同时测试，得到多组参数
    optuna_params = finetune(
        stra,
        method='Sko',
        # stocks=['600519.SH', '000001.SZ', '300750.SZ'],
        # stocks=['600051.SH'],
        stocks=code_list[:20],
        # stocks=['600519.SH', '000001.SZ', '300750.SZ'],
        fromdate=datetime(2024, 1, 1),
        todate=datetime(2025, 4, 1),
        count=1

    )
```
选策略：stra,获取股票列表：   
```python
code_list = xtdata.get_stock_list_in_sector('上证A股')
```
然后对所有股票进行回测，根据平均收益率，得到一个最优参数

！[1](twt_code/pic/1.png)

#  validation

```python

    validation(
        selected_strategy=stra,
        stocks=['600519.SH', '000001.SZ', '300750.SZ'],
        fromdate=datetime(2023, 1, 1),
        todate=datetime(2025, 4, 1),
        optimized_params=optuna_params,

    )
```
得到finetune的参数，对stocks股票列表进行验证，对股票排序，返回收益top的股票列表

！[2](twt_code/pic/2.png)

# validation_cross

    top_stocks = validation_cross(
        selected_strategy=stra,
        stocks=['600519.SH', '000001.SZ', '300750.SZ'],
        optimized_params=optuna_params,
        fromdate=datetime(2023, 1, 1),
        todate=datetime(2025, 4, 1),
        window_months=3,
        step_months=2
    )

交叉验证验证：
根据方法：
```python
def generate_test_periods(fromdate, todate, window_months=3, step_months=1):
    """生成按指定步长滚动的测试时间段"""
    test_periods = []
    current_start = fromdate
    while current_start < todate:
        # 计算窗口结束日期
        current_end = current_start + relativedelta(months=+window_months)
        if current_end > todate:
            break
            # current_end = todate
        test_periods.append((current_start, current_end))

        # 移动到下一个窗口的起始日期
        current_start = current_start + relativedelta(months=+step_months)
    return test_periods
```
把回测时间分为n个区间，每只股票在每个时间区间回测后的平均收益率排序，返回top的股票列表

！[3](twt_code/pic/3.png)

# back_test

```python
    back_test(
        selected_strategy=stra,
        stocks=['600519.SH', '000001.SZ', '300750.SZ'],
        optimized_params=optuna_params,

    )

```
接受最优的参数和选定的股票，进行最近时间的test

# 注意事项：

1.调参的时候参数的范围可能得认为设定：这里默认0~50，但这可能与交叉验证时间区间小于参数，即数据不足会报错，比如时间区间一个月为，均线参数为40天

2.实盘交易，如果需要在最近的一天下单，需要在策略里进行相关代码书写，逻辑为如果满足购买条件并且日期为当天才发送保单，或者人工下单最为保险