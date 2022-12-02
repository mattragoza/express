import numpy as np


def express(obj):
    if isinstance(obj, Expression):
        return obj
    elif isinstance(obj, str):
        return [Variable(o) for o in obj.split()]
    else:
        return Constant(obj)


class Expression(object):

    def __init__(self, *args):
        self.args = args

    def __repr__(self):
        type_name = type(self).__name__
        arg_reprs = map(repr, self.args)
        return f'{type_name}({", ".join(arg_reprs)})'

    def __neg__(self):
        return Neg(self)

    def __add__(self, other):
        if other == 0:
            return self
        elif self == 0:
            return other
        return Add(self, other)

    def __sub__(self, other):
        return Add(self, -other)

    def __mul__(self, other):
        if other == 0:
            return other
        elif self == 0:
            return self
        elif other == 1:
            return self
        elif self == 1:
            return other
        return Mul(self, other)


class Constant(Expression):

    def __init__(self, *args, **kwargs):
        self.value = np.array(*args, **kwargs)

    def __repr__(self):
        return repr(self.value)[6:-1].replace('\n      ', '')

    def __eq__(self, other):
        return self.value == other

    def eval(self, **vars):
        return self.value

    def diff(self, wrt):
        return Constant(0)


class Variable(Expression):

    def __init__(self, name):
        self.name = str(name)

    def __repr__(self):
        return self.name

    def eval(self, **vars):
        return vars.get(self.name, self)

    def diff(self, wrt):
        return Constant(int(wrt.name == self.name))


class Neg(Expression):

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
        deriv = Constant(0)
        for i, arg in enumerate(self.args):
            if i == 0:
                deriv = arg.diff(wrt)
            else:
                deriv += arg.diff(wrt)
        return deriv


class Mul(Expression):

    def __repr__(self):
        return ''.join(map(repr, self.args))
    
    def eval(self, **vars):
        value = 1
        for i, arg in enumerate(self.args):
            if i == 0:
                value = arg.eval(**vars)
            else:
                value += arg.eval(**vars)
        return value

    def diff(self, wrt):
        deriv = Constant(0)
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


class Deriv(Expression):

    def __init__(self, wrt, arg=None):
        self.arg = arg
        self.wrt = wrt

    def __repr__(self):
        if self.arg is None:
            return f'∂/∂{repr(self.wrt)}'
        else:
            return f'∂/∂{repr(self.wrt)} {repr(self.arg)}'

    def __mul__(self, other):
        if self.arg is None:
            return Deriv(self.wrt, arg=other)
        else:
            super().__mul__(self, other)

    def eval(self, **vars):
        return self.arg.diff(wrt=self.wrt)


# spatial coordinates
x1, x2, x3, κ = express('x₁ x₂ x₃ κ')

# deformation field
u = np.array([x1 + κ * x2, x2, x3])

# del operator
D = np.array([
    Deriv(wrt=x1),
    Deriv(wrt=x2),
    Deriv(wrt=x3)
])

# deformation gradient
F = np.outer(D, u).T

# evaluate the deriatives
for i in range(3):
    for j in range(3):
        F[i,j] = F[i,j].eval()

# Piola stess tensor
A, B, C, τ = express('A B C τ')
o = express(0)
p, q, r = τ - B*κ, o, o #express('p q r')
P = np.array([
    [A, τ, o],
    [p, B, o],
    [q, r, C]
])

# second equation of motion
P @ F.T - F @ P.T

# inverse of defomration gradient
l = express(1)
Finv = np.array([
    [l, -κ, o],
    [o, l, o],
    [o, o, l]
])
F @ Finv

# symmetric Piola tensor
S = Finv @ P

# unit vectors
e1 = np.array([l, o, o])
e2 = np.array([o, l, o])
e3 = np.array([o, o, l])

print(P)
print(e1)
print(P @ e1)
print(P @ e2)
print(P @ e3)
