
package observable.orderbook {
    @python.intrinsic.function("Proxies", "N/A", "orderbook.of_trader._OfTrader_Impl")
    def OfTrader(Trader = trader.SingleProxy()) : IOrderBook
        
    
    @python.intrinsic.function("Queue's", "Asks(%(book)s)", "orderbook.queue._Asks_Impl")
    def Asks(book = OfTrader()) : IOrderQueue
        
    
    @python.intrinsic.function("Queue's", "Bids(%(book)s)", "orderbook.queue._Bids_Impl")
    def Bids(book = OfTrader()) : IOrderQueue
        
    
    @python.intrinsic.observable("Orderbook", "Price(%(queue)s)", "orderbook.props._BestPrice_Impl")
    def BestPrice(queue = Asks()) : IObservable
        
    
    @python.observable("Orderbook", "Ask_{%(book)s}")
    def AskPrice(book = OfTrader())
         = BestPrice(Asks(book))
    
    @python.observable("Orderbook", "Bid^{%(book)s}")
    def BidPrice(book = OfTrader())
         = BestPrice(Bids(book))
    
    @python.intrinsic.observable("Orderbook", "LastPrice(%(queue)s)", "orderbook.last_price._LastPrice_Impl")
    def LastPrice(queue = Asks()) : IObservable
        
    
    @python.observable("Orderbook", "Ask_{%(book)s}")
    def AskLastPrice(book = OfTrader())
         = LastPrice(Asks(book))
    
    @python.observable("Orderbook", "Bid^{%(book)s}")
    def BidLastPrice(book = OfTrader())
         = LastPrice(Bids(book))
    
    @python.intrinsic.observable("Orderbook", "LastTradePrice(%(queue)s)", "orderbook.last_trade._LastTradePrice_Impl")
    def LastTradePrice(queue = Asks()) : IObservable
        
    
    @python.intrinsic.observable("Orderbook", "LastTradeVolume(%(queue)s)", "orderbook.last_trade._LastTradeVolume_Impl")
    def LastTradeVolume(queue = Asks()) : IObservable
        
    
    def PriceAtVolume(queue = Asks(),
                      volume = 100.0) : () => Float
        
    
    @python.observable("Orderbook", "Price_{%(alpha)s}^{%(queue)s}")
    def WeightedPrice(queue = Asks(),
                      alpha = 0.015)
         = EWMA(LastTradePrice(queue)*LastTradeVolume(queue),alpha)/EWMA(LastTradeVolume(queue),alpha)
    
    @python.observable("Orderbook", "Ask_{%(alpha)s}^{%(book)s}")
    def AskWeightedPrice(book = OfTrader(),
                         alpha = 0.015)
         = WeightedPrice(Asks(book),alpha)
    
    @python.observable("Orderbook", "Bid_{%(alpha)s}^{%(book)s}")
    def BidWeightedPrice(book = OfTrader(),
                         alpha = 0.015)
         = WeightedPrice(Bids(book),alpha)
    
    def TickSize(book = OfTrader()) : () => Float
        
    
    @python.observable("Orderbook", "Spread_{%(book)s}")
    def Spread(book = OfTrader())
         = AskPrice(book)-BidPrice(book)
    
    @python.observable("Orderbook", "MidPrice_{%(book)s}")
    def MidPrice(book = OfTrader())
         = (AskPrice(book)+BidPrice(book))/2.0
}
