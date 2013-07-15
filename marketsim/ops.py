from marketsim import meta, Side, types, registry, getLabel, event, _
import marketsim
import math, inspect 

def convert(other):
    if type(other) in [int, float]:
        other = constant(other)
    return other


class Function_impl(object):
    
    def __add__(self, other):
        return Sum(self, convert(other))
    
    def __sub__(self, other):
        return Sub(self, convert(other))
    
    def __mul__(self, other):
        return Product(self, convert(other))
    
    def __div__(self, other):
        return Div(self, convert(other))
    
    def __lt__(self, other):
        return less(self, convert(other))
    
    def __gt__(self, other):
        return greater(self, convert(other))
    
    def __eq__(self, other):
        return equal(self, convert(other))
    
    def __ne__(self, other):
        return notequal(self, convert(other))

Function = types.Factory("Function", """(Function_impl, types.IFunction[%(T)s]):
    T = %(T)s
""", globals())   

class BinaryOp_Impl(object):
    
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs 
        if types.IEvent in inspect.getmro(type(lhs)):
            event.subscribe(lhs, _(self).fire, self)
        if types.IEvent in inspect.getmro(type(rhs)):
            event.subscribe(rhs, _(self).fire, self)
            
    def __call__(self):
        lhs = self.lhs()
        rhs = self.rhs()
        return self._call(lhs, rhs) if lhs is not None and rhs is not None else None

    @property
    def label(self):
        return self.lhs.label + self.sign + self.rhs.label
    
    def __repr__(self):
        return repr(self.lhs) + self.sign + repr(self.rhs)

BinaryOp = types.Factory("BinaryOp", """(BinaryOp_Impl, Function[%(T)s], types.Observable[%(T)s]):
    def __init__(self, lhs, rhs):
        BinaryOp_Impl.__init__(self, lhs, rhs)
        types.Observable[%(T)s].__init__(self)

    _properties = [('lhs', meta.function((), %(T)s)), 
                   ('rhs', meta.function((), %(T)s))]
       
    @property
    def attributes(self):
        return {}
""", globals())
    
#---------------------------------------------- Condition 
        
class Condition_Impl(object):
    
    def __init__(self, cond, ifpart, elsepart):
        self.cond = cond
        self.ifpart = ifpart
        self.elsepart = elsepart
        
    def __call__(self):
        c = self.cond()
        return None if c is None else self.ifpart() if c else self.elsepart()
    
    def __repr__(self):
        return 'if ' + repr(self.cond) + ' then ' + repr(self.ifpart) + ' else ' + repr(self.elsepart)

Condition = types.Factory("Condition", """(Condition_Impl, Function[%(T)s]):

    def __init__(self, cond, ifpart, elsepart):
        Condition_Impl.__init__(self, cond, ifpart, elsepart)
        self._alias = ['Condition[%(T)s]']
        
    _types = [meta.function((), %(T)s)]
        
    _properties = [('cond', meta.function((), bool)), 
                   ('ifpart', meta.function((), %(T)s)), 
                   ('elsepart', meta.function((), %(T)s))]
""", globals())

class _Conditional_Base(Function[bool]):
    
    def __getitem__(self, (ifpart, elsepart)):
        T = getattr(ifpart, 'T', getattr(elsepart, 'T', None))
        if T is None:
            print "cannot infer expression type from ", ifpart, ' and ', elsepart
        return Condition[T](self, ifpart, elsepart)

# ---------------------------------------------------- Equal

class _Equal_Impl(_Conditional_Base):
    
    sign = "=="
    
    def _call(self):
        return lhs == rhs

Equal = types.Factory("Equal", """(BinaryOp[%(T)s], _Equal_Impl):
    BranchType = %(T)s
""", globals())

def logic_op(T):
    def inner(lhs, rhs):
        if 'T' in dir(lhs):
            if 'T' in dir(rhs):
                assert lhs.T == rhs.T
            return T[lhs.T](lhs, rhs)
        if 'T' in dir(rhs):
            return T[rhs.T](lhs, rhs)
        raise "Cannot inference T for " + repr(lhs) + ' ' + T.sign + ' ' + repr(rhs)
    return inner

equal = logic_op(Equal)
        
# ---------------------------------------------------- NotEqual

class _NotEqual_Impl(_Conditional_Base):
    
    sign = "!="
    
    def _call(self, lhs, rhs):
        return lhs != rhs

NotEqual = types.Factory("NotEqual", """(BinaryOp[%(T)s], _NotEqual_Impl):
    BranchType = %(T)s
""", globals())

notequal = logic_op(NotEqual)
        
# ---------------------------------------------------- Greater

class _Greater_Impl(_Conditional_Base):
    
    sign = ">"
    
    def _call(self, lhs, rhs):
        return lhs > rhs

Greater = types.Factory("Greater", """(BinaryOp[%(T)s], _Greater_Impl):
    BranchType = %(T)s
""", globals())

greater = logic_op(Greater)
    
# ---------------------------------------------------- Less

class _Less_Impl(_Conditional_Base):
    
    sign = "<"
    
    def _call(self, lhs, rhs):
        return lhs < rhs

Less = types.Factory("Less", """(BinaryOp[%(T)s], _Less_Impl):
    BranchType = %(T)s
""", globals())

less = logic_op(Less)
    
# ---------------------------------------------------- Constant

# NB! _None is a special case of Constant but we don't use the latter 
# since we don't want to show Nones in the web-interface and in the object graph

class _None_Impl(object):
    
    def __call__(self):
        return None
    
    def __repr__(self):
        return 'None'

_None = types.Factory('_None', """(_None_Impl, Function[%(T)s]):""", globals())

# ---------------------------------------------------- Constant

class _Constant_Impl(object):
    """ Constant function returning **value**.
    """
    
    def _casts_to(self, dst):
        if type(dst) is meta.function:
            rv = dst.rv
            return rv is float or\
                (type(rv) is meta.greater_or_equal and rv._bound <= self.value) or\
                (type(rv) is meta.greater_than and rv._bound < self.value) or\
                (type(rv) is meta.less_or_equal and rv._bound >= self.value) or\
                (type(rv) is meta.less_than and rv._bound > self.value)
        return False 
        
    def __call__(self, *args, **kwargs):
        return self.value
    
    @property
    def label(self):
        return str(self.value)
    
    def __repr__(self):
        return "constant("+repr(self.value)+")"
    
_defaults = { float: 100, Side : Side.Sell }

Constant = types.Factory('Constant', """(_Constant_Impl, Function[%(T)s]):
    \""" Constant function returning **value**.
    \"""
    def __init__(self, value = _defaults[%(T)s]):
        self.value = value
    
    _properties = {'value' : %(T)s}
""", globals())

def constant(x):
    return Constant[float](x) if type(x) is float\
        else Constant[float](x) if type(x) is int\
        else Constant[Side](x) if x is Side.Sell or x is Side.Buy\
        else None    


@registry.expose(['Arithmetic', 'negate'])
class negate(Function[float]):
    """ Function returning Product of the operands
    """
    
    def __init__(self, arg=constant(1.)):
        self.arg = arg
        
    _properties = { "arg" : types.IFunction[float] }
    
    def __call__(self, *args, **kwargs):
        x = self.arg()
        return -x if x is not None else None
    
    def __repr__(self):
        return "-" + repr(self.arg)
    
@registry.expose(['Arithmetic', 'sqrt'])
class sqrt(Function[float]):
    """ Function returning square root of the operand
    """
    
    def __init__(self, arg=constant(1.)):
        self.arg = arg
        
    _properties = { "arg" : types.IFunction[float] }
    
    def __call__(self, *args, **kwargs):
        x = self.arg()
        return math.sqrt(x) if x is not None else None
    
    @property
    def label(self):
        return "\sqrt{" + self.arg.label + "}"
    
    def __repr__(self):
        return "sqrt(" + repr(self.arg) + ")"



@registry.expose(['Arithmetic', 'identity'])
class identity(Function[float]):
    
    def __init__(self, arg=constant(1.)):
        self.arg = arg
        
    _properties = { "arg" : types.IFunction[float] }
    
    def __call__(self, *args, **kwargs):
        return self.arg()
    
    def __repr__(self):
        return "id(" + repr(self.arg) + ")"
    
@registry.expose(['Arithmetic', '*'], args = (constant(1.), constant(1.)))
class Product(BinaryOp[float]):
    """ Function returning product of the operands
    """
    
    sign = '*'
    
    def __init__(self, lhs, rhs):
        BinaryOp[float].__init__(self, lhs, rhs)
    
    def _call(self, lhs, rhs):
        return lhs * rhs
    
class Sqr(types.Observable[float]):
    
    def __init__(self, source):
        self._source = source
        types.Observable[float].__init__(self)
        self._event = event.subscribe(source, _(self).fire, self)
        
    _properties = { 'source' : types.IObservable[float] }
    
    @property
    def source(self):
        return self._source
    
    def __call__(self):
        r = self._source()
        return r*r if r is not None else None

@registry.expose(['Arithmetic', '+'], args = (constant(1.), constant(1.)))    
class Sum(BinaryOp[float]):
    """ Function returning Sum of the operands
    """
    
    def __init__(self, lhs, rhs):
        BinaryOp[float].__init__(self, lhs, rhs)
    
    def _call(self, lhs, rhs):
        return lhs + rhs

    sign = '+'         

@registry.expose(['Arithmetic', '/'], args = (constant(1.), constant(1.)))
class Div(BinaryOp[float]):
    """ Function returning division of the operands
    """
    def __init__(self, lhs, rhs):
        BinaryOp[float].__init__(self, lhs, rhs)
    
    def _call(self, lhs, rhs):
        return lhs / rhs if rhs != 0 else None
    
    sign = '/'
    
    @property
    def label(self):
        return '\\frac{'+self.lhs.label+'}{'+self.rhs.label+'}'

@registry.expose(['Arithmetic', '-'], args = (constant(1.), constant(1.)))    
class Sub(BinaryOp[float]):
    """ Function substructing the right operand from the left one
    """
    
    def __init__(self, lhs, rhs):
        BinaryOp[float].__init__(self, lhs, rhs)
    
    def _call(self, lhs, rhs):
        return lhs - rhs
    
    sign = '-'

class Derivative(Function[float]):
    
    def __init__(self, source):
        self.source = source
        
    @property
    def attributes(self):
        return {}
        
    _properties = { 'source' : types.IDifferentiable }
    
    @property
    def label(self):
        return '\\frac{d' + getLabel(self.source) + '}{dt}'
        
    def __call__(self):
        return self.source.derivative()
   
