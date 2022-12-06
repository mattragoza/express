import numpy as np


def express(obj):
    if isinstance(obj, Expression):
        return obj
    elif isinstance(obj, (list, tuple)):
        return Tensor(obj)
    elif isinstance(obj, str):
        objs = obj.split()
        if len(objs) > 1:
            return [Symbol(o) for o in objs]
        elif len(objs) == 1:
            return Symbol(objs[0])
    elif isinstance(obj, (int, float)):
        return Number(obj)
    raise TypeError(f'cannot express {type(obj)}')


class Expression(object):

    def __init__(self, *args):
        self.args = args

    def __repr__(self):
        type_name = type(self).__name__
        arg_reprs = map(repr, self.args)
        return f'{type_name}({", ".join(arg_reprs)})'

    def __neg__(self):
        if self == 0:
            return self
        elif isinstance(self, Tensor):
            return Tensor([-a for a in self])
        return Negative(self)

    def __add__(self, other):
        if other == 0:
            return self
        elif self == 0:
            return other
        elif isinstance(self, Tensor) and isinstance(other, Tensor):
            same_shape = self.shape == other.shape
            assert same_shape, 'cannot add tensors of different shapes'
            return Tensor([a + b for a, b in zip(self, other)])
        elif isinstance(self, Tensor):
            return Tensor([a + other for a in self])
        elif isinstance(other, Tensor):
            return Tensor([self + b for b in other])
        return Add(self, other)

    def __radd__(self, other):
        return Expression.__add__(other, self)

    def __sub__(self, other):
        if isinstance(self, Tensor) and isinstance(other, Tensor):
            same_shape = self.shape == other.shape
            assert same_shape, 'cannot subtract tensors of different shapes'
            return Tensor([a - b for a, b in zip(self, other)])
        elif isinstance(self, Tensor):
            return Tensor([a - other for a in self])
        elif isinstance(other, Tensor):
            return Tensor([self - b for b in other])
        return Add(self, -other)

    def __rsub__(self, other):
        return Expression.__sub__(other, self)

    def __mul__(self, other):
        both_tensors = isinstance(self, Tensor) and isinstance(other, Tensor)
        assert not both_tensors, 'cannot multiply two tensors'
        if other == 1:
            return self
        elif self == 1:
            return other
        elif isinstance(self, Tensor):
            return Tensor([a * other for a in self])
        elif isinstance(other, Tensor):
            return Tensor([self * a for a in other])
        elif other == 0:
            return other
        elif self == 0:
            return self
        return Multiply(self, other)

    def __rmul__(self, other):
        return Expression.__mul__(other, self)

    def asarray(self):
        return self

    @property
    def order(self):
        return 0

    @property
    def shape(self):
        return ()

    def inner(self, other):
        both_tensors = isinstance(self, Tensor) and isinstance(other, Tensor)
        if not both_tensors:
            return self * other
        elif self.order > 1 and other.order > 1:
            return Tensor([a.inner(b) for a, b in zip(self, other)])
        elif self.order > 1:
            return Tensor([a.inner(other) for a in self])
        elif other.order > 1:
            return Tensor([self.inner(b) for b in other])
        return Add(*[a * b for a, b in zip(self, other)])

    def outer(self, other):
        both_tensors = isinstance(self, Tensor) and isinstance(other, Tensor)
        if not both_tensors:
            return self * other
        elif self.order > 1 or other.order > 1:
            raise NotImplementedError
        return Tensor([Tensor([a * b for b in other]) for a in self])

    @property
    def T(self):
        if self.order > 2:
            return Tensor([a.T for a in self])
        elif self.order == 2:
            return Tensor(zip(*self.args))
        else:
            return self


class Number(Expression):

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return repr(self.value)

    def __eq__(self, other):
        return self.value == other

    def eval(self, **vars):
        return self.value

    def diff(self, wrt):
        if isinstance(wrt, Tensor):
            return Tensor([self.diff(a) for a in wrt.args])
        return Number(0)


class Symbol(Expression):

    def __init__(self, name):
        self.name = str(name)

    def __repr__(self):
        return self.name

    def eval(self, **vars):
        return vars.get(self.name, self)

    def diff(self, wrt):
        if isinstance(wrt, Tensor):
            return Tensor([self.diff(a) for a in wrt.args])
        elif isinstance(wrt, Symbol):
            if wrt.name == self.name:
                return Number(1)
        return Derivative(wrt, arg=self)


class Negative(Expression):

    def __init__(self, arg):
        self.arg = arg

    def __repr__(self):
        return f'-{repr(self.arg)}'

    def eval(self, **vars):
        return -self.arg.eval(**vars)

    def diff(self, wrt):
        return -self.arg.diff(wrt)


class Add(Expression):

    def __repr__(self):
        return '(' + ' + '.join(map(repr, self.args)) + ')'

    def eval(self, **vars):
        value = 0
        for i, arg in enumerate(self.args):
            if i == 0:
                value = arg.eval(**vars)
            else:
                value += arg.eval(**vars)
        return value

    def diff(self, wrt):
        deriv = Number(0)
        for i, arg in enumerate(self.args):
            if i == 0:
                deriv = arg.diff(wrt)
            else:
                deriv += arg.diff(wrt)
        return deriv


class Multiply(Expression):

    def __repr__(self):
        return ''.join(map(repr, self.args))
    
    def eval(self, **vars):
        value = 1
        for i, arg in enumerate(self.args):
            if i == 0:
                value = arg.eval(**vars)
            else:
                value *= arg.eval(**vars)
        return value

    def diff(self, wrt):
        deriv = Number(0)
        for i, arg in enumerate(self.args):
            term = arg.diff(wrt)
            for j, arg in enumerate(self.args):
                if j != i:
                    term = term * arg
            if i == 0:
                deriv = term
            else:
                deriv += term
        return deriv


class Derivative(Expression):

    def __init__(self, wrt, arg=None):
        self.arg = arg
        self.wrt = wrt

    def __repr__(self):
        wrt_repr = repr(self.wrt)
        if self.arg is None:
            return f'd/d{wrt_repr}'
        arg_repr = repr(self.arg)
        if isinstance(self.arg, (Symbol, Number)):
            return f'd{arg_repr}/d{wrt_repr}'
        return f'(d/d{wrt_repr} {arg_repr})'

    def __mul__(self, other):
        if self.arg is None:
            return Derivative(self.wrt, arg=other)
        return Expression.__mul__(self, other)

    def eval(self, **vars):
        if self.arg is None:
            return self
        return self.arg.diff(self.wrt).eval(**vars)

    def diff(self, wrt):
        if isinstance(wrt, Tensor):
            return Tensor([Derivative(wrt=a, arg=self) for a in wrt.args])
        return Derivative(wrt, arg=self)


class Tensor(Expression):

    def __init__(self, args):
        self.args = [express(a) for a in args]
        assert len(self.args) > 0, 'cannot create empty tensor'
        assert len(set(a.shape for a in self.args)) == 1, \
            'tensor components must be same shape'

    def __repr__(self):
        return str(self.asarray())

    def __getitem__(self, idx):
        return self.args[idx]

    def __iter__(self):
        return iter(self.args)

    def __len__(self):
        return len(self.args)

    def asarray(self):
        return np.asarray([a.asarray() for a in self.args])

    @property
    def order(self):
        return self.args[0].order + 1

    @property
    def shape(self):
        return (len(self.args),) + self.args[0].shape

    def eval(self, **vars):
        value = [a.eval(**vars) for a in self.args]
        if any(isinstance(v, Expression) for v in value):
            return Tensor(value)
        return np.array(value)

    def diff(self, wrt):
        return Tensor([a.diff(wrt) for a in self.args])
