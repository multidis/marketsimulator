from marketsim import event, _, meta, types, registry, ops, observable

class Base(object):

    def bind(self, context):
        self._strategies = context.strategies
        self._weights = self.zeros()
        
    def __call__(self):
        return self.update()
    
    def zeros(self):
        return [ 0 for _ in xrange(0, len(self._strategies))]
    
    def ones(self):
        return [ 1 for _ in xrange(0, len(self._strategies))]
    
    def update(self):
        self._weights = self.getWeights()
        return self._weights

@registry.expose(['Efficiency'])       
class Efficiency(Base):
        
    def getWeights(self):
        return [ max(s[3](), 0) for s in self._strategies]
    
import _trade_if_profitable

def normalized(f, base = 1.002):
    return ops.Atan(ops.Pow(ops.constant(base), f))

def cachedattr(obj, name, setter):
    if not hasattr(obj, name):
        setattr(obj, name, setter())
        
    return getattr(obj, name)

@meta.sig(args=(types.ISingleAssetStrategy,), rv=types.IFunction[float])
def efficiencyTrend(strategy):
    return cachedattr(strategy, '_efficiencyTrendNormalized', 
                      lambda: normalized(
                                _trade_if_profitable.efficiencyTrend2(
                                    _trade_if_profitable.Estimator(strategy))))


@meta.sig(args=(types.ISingleAssetStrategy,), rv=types.IFunction[float])
def efficiency(strategy):
    return cachedattr(strategy, '_efficiencyNormalized', 
                      lambda: normalized(
                                _trade_if_profitable.efficiency(
                                    _trade_if_profitable.Estimator(strategy))))

@meta.sig(args=types.listOf(float), rv=types.listOf(float))
def no(weights):
    return weights

@meta.sig(args=types.listOf(float), rv=types.listOf(float))
def chooseTheBest(weights):
    mw = max(weights)
    # index of the strategy with the highest (positive) efficiency
    max_idx = weights.index(mw)
    weights = [0] * len(weights)
    
    if mw > 0:
        weights[max_idx] = 1
    
    return weights

class Score(ops.Function[float]):
    
    def __init__(self, trader):
        self._efficiency = observable.Efficiency(trader)
        event.subscribe(
                observable.OnEveryDt(1, self._efficiency),
                 _(self)._update, self)
        self._score = 1
        self._last = 0
        
    def _update(self, dummy):
        e = self._efficiency()
        if e is not None:
            delta = e - self._last
            if delta > 0: self._score += 1
            if delta < 0 and self._score > 1: self._score -= 1
        
    def __call__(self):
        return self._score
    
from _account import Account

@meta.sig(args=(types.ISingleAssetStrategy,), rv=types.IFunction[float])
def score(strategy):
    return cachedattr(strategy, '_score', 
                      lambda: Score(Account(strategy)))

@registry.expose(['Efficiency alpha'])       
class EfficiencyAlpha(Efficiency):
    
    def __init__(self, alpha=0.5):
        self.alpha = alpha
        
    _properties = { 'alpha' : types.less_than(1., types.non_negative) }

    def getWeights(self):
        old = self._weights
        new = super(EfficiencyAlpha, self).getWeights()
        return [ self.alpha * x + (1 - self.alpha) * y for x, y in zip(old, new)]
    
@registry.expose(['Track record'])       
class TrackRecord(Efficiency):
    
    def getWeights(self):
        new = super(TrackRecord, self).getWeights()
        return [ x + (y > 0) for x, y in zip(self._weights, new)]
    
@registry.expose(['Choose the best'])       
class ChooseTheBest(Efficiency):
    
    def getWeights(self):
        w = super(ChooseTheBest, self).getWeights()
        mw = max(w)
        # index of the strategy with the highest (positive) efficiency
        max_idx = w.index(mw)
        weights = self.zeros()
        
        if mw > 0:
            weights[max_idx] = 1
        
        return weights
    
@registry.expose(['Uniform'])       
class Uniform(Base):
    
    def bind(self, context):
        self._weights = self.ones()
    
    def getWeights(self):
        return self._weights

@meta.sig(args=(types.IAccount,), rv=types.IFunction[float])
def unit(trader):
    return ops.constant(1.)

