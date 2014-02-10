def WithExpiry(expiry = None,proto = None): 
    from marketsim import IFunction
    from marketsim import rtti
    from marketsim import float
    from marketsim import IOrderGenerator
    from marketsim import Side
    from marketsim.gen._out.order._curried._sideprice_withexpiry import sideprice_WithExpiry_IFunctionFloatSideFloatIOrderGenerator as _order__curried_sideprice_WithExpiry
    if expiry is None or rtti.can_be_casted(expiry, IFunction[float]):
        if proto is None or rtti.can_be_casted(proto, IFunction[IOrderGenerator,IFunction[Side]
        ,IFunction[float]]):
            return _order__curried_sideprice_WithExpiry(expiry,proto)
    raise Exception("Cannot find suitable overload")