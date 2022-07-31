import datetime
import backtrader as bt

class MAcrossover(bt.Strategy): 
#移动平均参数
    params = (('pfast',20),('pslow',50),)
    
    def log(self, txt, dt=None):     
        dt = dt or self.datas[0].datetime.date(0)     
    #    print('%s, %s' % (dt.isoformat(), txt))  # 执行策略优化时 可注释掉此行

    def __init__(self):     
        self.dataclose = self.datas[0].close     
        # Order变量包含持仓数据与状态
        self.order = None     
        # 初始化移动平均数据     
        self.slow_sma = bt.indicators.MovingAverageSimple(self.datas[0],                                       
                        period=self.params.pslow)     
        self.fast_sma = bt.indicators.MovingAverageSimple(self.datas[0], 
                        period=self.params.pfast)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            #主动买卖的订单提交或接受时  - 不触发
            return
        #验证订单是否完成
        #注意: 当现金不足时，券商可以拒绝订单
        if order.status in [order.Completed]:
            if order.isbuy():             
                self.log('BUY EXECUTED, %.2f' % order.executed.price)         
            elif order.issell():             
                self.log('SELL EXECUTED, %.2f' % order.executed.price)
            self.bar_executed = len(self)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')     
        #重置订单
        self.order = None
    
    def next(self):
        # 检测是否有未完成订单
        if self.order:
            return
        #验证是否有持仓
        if not self.position:
        #如果没有持仓，寻找开仓信号
            #SMA快线突破SMA慢线
            if self.fast_sma[0] > self.slow_sma[0] and self.fast_sma[-1] < self.slow_sma[-1]:
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                #继续追踪已经创建的订单，避免重复开仓
                self.order = self.buy()
            #如果SMA快线跌破SMA慢线
            elif self.fast_sma[0] < self.slow_sma[0] and self.fast_sma[-1] > self.slow_sma[-1]:
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                #继续追踪已经创建的订单，避免重复开仓
                self.order = self.sell()
        else:
            # 如果已有持仓，寻找平仓信号
            if len(self) >= (self.bar_executed + 5):
                self.log('CLOSE CREATE, %.2f' % self.dataclose[0])
                self.order = self.close()     