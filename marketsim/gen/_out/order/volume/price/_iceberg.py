def Iceberg(lotSize = None,proto = None): 
    from marketsim import IFunction
    from marketsim import rtti
    from marketsim import float
    from marketsim import IOrderGenerator
    from marketsim.gen._out.order._curried._volume_price_iceberg import volume_price_Iceberg_IFunctionFloatFloatFloatIOrderGenerator as _order__curried_volume_price_Iceberg
    if lotSize is None or rtti.can_be_casted(lotSize, IFunction[float]):
        if proto is None or rtti.can_be_casted(proto, IFunction[IFunction[IOrderGenerator,IFunction[float]],IFunction[float]]):
            return _order__curried_volume_price_Iceberg(lotSize,proto)
    raise Exception("Cannot find suitable overload")