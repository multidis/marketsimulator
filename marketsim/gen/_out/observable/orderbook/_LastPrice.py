from marketsim import registry
from marketsim.gen._intrinsic.orderbook.last_price import _LastPrice_Impl
from marketsim import IOrderQueue
@registry.expose(["Orderbook", "LastPrice"])
class LastPrice(_LastPrice_Impl):
    """ 
    """ 
    def __init__(self, queue = None):
        from marketsim.gen._out.observable.orderbook._Asks import Asks
        from marketsim import event
        from marketsim import types
        self.queue = queue if queue is not None else Asks()
        if isinstance(queue, types.IEvent):
            event.subscribe(self.queue, self.fire, self)
        _LastPrice_Impl.__init__(self)
    
    @property
    def label(self):
        return repr(self)
    
    _properties = {
        'queue' : IOrderQueue
    }
    def __repr__(self):
        return "LastPrice(%(queue)s)" % self.__dict__
    
