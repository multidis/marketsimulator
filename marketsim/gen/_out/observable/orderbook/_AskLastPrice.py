from marketsim import registry
from marketsim.ops._all import Observable
from marketsim import IOrderBook
from marketsim import context
@registry.expose(["Orderbook", "AskLastPrice"])
class AskLastPrice(Observable[float]):
    """ 
    """ 
    def __init__(self, book = None):
        from marketsim.gen._out.observable.orderbook._OfTrader import OfTrader
        from marketsim import _
        from marketsim import event
        Observable[float].__init__(self)
        self.book = book if book is not None else OfTrader()
        self.impl = self.getImpl()
        event.subscribe(self.impl, _(self).fire, self)
    
    @property
    def label(self):
        return repr(self)
    
    _properties = {
        'book' : IOrderBook
    }
    def __repr__(self):
        return "Ask_{%(book)s}" % self.__dict__
    
    _internals = ['impl']
    @property
    def attributes(self):
        return {}
    
    def getImpl(self):
        from marketsim.gen._out.observable.orderbook._LastPrice import LastPrice
        from marketsim.gen._out.observable.orderbook._Asks import Asks
        return LastPrice(Asks(self.book))
        
    
    def bind(self, ctx):
        self._ctx = ctx.clone()
    
    def reset(self):
        self.impl = self.getImpl()
        ctx = getattr(self, '_ctx', None)
        if ctx: context.bind(self.impl, ctx)
    
    def __call__(self, *args, **kwargs):
        return self.impl()
    
