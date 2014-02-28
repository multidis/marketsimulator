from marketsim.gen._out._ifunction._ifunctioniobservableiorder_from_ifunctionside import IFunctionIObservableIOrder_from_IFunctionSide
from marketsim.gen._out._ievent import IEvent
from marketsim.gen._out._isingleassetstrategy import ISingleAssetStrategy
from marketsim import registry
from marketsim import context
@registry.expose(["Strategy", "TrendFollower"])
class TrendFollower_IEventSideIObservableIOrderFloatFloat(ISingleAssetStrategy):
    """  where the *signal* is a trend of the asset.
     Under trend we understand the first derivative of some moving average of asset prices.
     If the derivative is positive, the trader buys; if negative - it sells.
     Since moving average is a continuously changing signal, we check its
     derivative at moments of time given by *eventGen*.
    """ 
    def __init__(self, eventGen = None, orderFactory = None, ewma_alpha = None, threshold = None):
        from marketsim import deref_opt
        from marketsim import _
        from marketsim import rtti
        from marketsim.gen._out.order._curried._side_market import side_Market_Float as _order__curried_side_Market_Float
        from marketsim.gen._out.event._every import Every_Float as _event_Every_Float
        from marketsim.gen._out.math.random._expovariate import expovariate_Float as _math_random_expovariate_Float
        from marketsim import event
        self.eventGen = eventGen if eventGen is not None else deref_opt(_event_Every_Float(deref_opt(_math_random_expovariate_Float(1.0))))
        self.orderFactory = orderFactory if orderFactory is not None else deref_opt(_order__curried_side_Market_Float())
        self.ewma_alpha = ewma_alpha if ewma_alpha is not None else 0.15
        self.threshold = threshold if threshold is not None else 0.0
        rtti.check_fields(self)
        self.impl = self.getImpl()
        self.on_order_created = event.Event()
        event.subscribe(self.impl.on_order_created, _(self)._send, self)
    
    @property
    def label(self):
        return repr(self)
    
    _properties = {
        'eventGen' : IEvent,
        'orderFactory' : IFunctionIObservableIOrder_from_IFunctionSide,
        'ewma_alpha' : float,
        'threshold' : float
    }
    def __repr__(self):
        return "TrendFollower(%(eventGen)s, %(orderFactory)s, %(ewma_alpha)s, %(threshold)s)" % self.__dict__
    
    def bind(self, ctx):
        self._ctx = ctx.clone()
    
    _internals = ['impl']
    def __call__(self, *args, **kwargs):
        return self.impl()
    
    def reset(self):
        self.impl = self.getImpl()
        ctx = getattr(self, '_ctx', None)
        if ctx: context.bind(self.impl, ctx)
    
    def getImpl(self):
        from marketsim.gen._out.strategy._generic import Generic_IObservableIOrderIEvent as _strategy_Generic_IObservableIOrderIEvent
        from marketsim.gen._out.strategy.side._trendfollower import TrendFollower_FloatFloatIOrderBook as _strategy_side_TrendFollower_FloatFloatIOrderBook
        from marketsim import deref_opt
        return deref_opt(_strategy_Generic_IObservableIOrderIEvent(deref_opt(self.orderFactory(deref_opt(_strategy_side_TrendFollower_FloatFloatIOrderBook(self.ewma_alpha,self.threshold)))),self.eventGen))
    
    def _send(self, order, source):
        self.on_order_created.fire(order, self)
    
def TrendFollower(eventGen = None,orderFactory = None,ewma_alpha = None,threshold = None): 
    from marketsim.gen._out._ievent import IEvent
    from marketsim.gen._out._ifunction._ifunctioniobservableiorder_from_ifunctionside import IFunctionIObservableIOrder_from_IFunctionSide
    from marketsim import rtti
    if eventGen is None or rtti.can_be_casted(eventGen, IEvent):
        if orderFactory is None or rtti.can_be_casted(orderFactory, IFunctionIObservableIOrder_from_IFunctionSide):
            if ewma_alpha is None or rtti.can_be_casted(ewma_alpha, float):
                if threshold is None or rtti.can_be_casted(threshold, float):
                    return TrendFollower_IEventSideIObservableIOrderFloatFloat(eventGen,orderFactory,ewma_alpha,threshold)
    raise Exception('Cannot find suitable overload for TrendFollower('+str(eventGen) +':'+ str(type(eventGen))+','+str(orderFactory) +':'+ str(type(orderFactory))+','+str(ewma_alpha) +':'+ str(type(ewma_alpha))+','+str(threshold) +':'+ str(type(threshold))+')')
