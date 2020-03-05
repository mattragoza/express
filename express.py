import numpy as np


class Expression(object):
    __array_priority__ = 1

    def __init__(self, *args):
        raise NotImplementedError

    def simplify(self):
        raise NotImplementedError
    
    def eval(self, **vars):
        raise NotImplementedError

    def diff(self, wrt):
        raise NotImplementedError

    def __add__(self, other):
        return Add(self, other)

    def __radd__(self, other):
        return Add(other, self)

    def __mul__(self, other):
        return Mul(self, other)

    def __rmul__(self, other):
        return Mul(other, self)


class Constant(Expression):

    def __init__(self, *args, **kwargs):
        self.value = np.array(*args, **kwargs)

    def __repr__(self):
        return type(self).__name__ + \
            repr(self.value)[5:].replace('\n       ', ' ')

    def __eq__(self, other):
        if isinstance(other, Constant):
            return self.value == other.value
        else:
            return self.value == other

    def eval(self, **vars):
        return self.value

    def diff(self, wrt):
        return Constant(0)

    def simplify(self):
        return self


class Variable(Expression):

    def __init__(self, name):
        self.name = str(name)

    def __repr__(self):
        return type(self).__name__ + '(' + self.name + ')'

    def __eq__(self, other):
        return isinstance(other, Variable) and self.name == other.name

    def eval(self, **vars):
        return vars.get(self.name, self)

    def diff(self, wrt):
        return Constant(1) if express(wrt) == self else Constant(0)

    def simplify(self):
        return self


class Add(Expression):

    def __init__(self, *args):
        self.args = [express(a) for a in args]

    def __repr__(self):
        return type(self).__name__ + '(' + ', '.join(map(repr, self.args)) + ')'

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

    def simplify(self):
        args = (a.simplify() for a in self.args)
        args = [a for a in args if a != 0]
        if len(args) > 1:
            return Add(*args)
        elif len(args) == 1:
            return args[0]
        else:
            return Constant(0)


class Mul(Expression):

    def __init__(self, *args):
        self.args = [express(a) for a in args]

    def __repr__(self):
        return type(self).__name__ + '(' + ', '.join(map(repr, self.args)) + ')'

    def eval(self, **vars):
        value = 1
        for i, arg in enumerate(self.args):
            if i == 0:
                value = arg.eval(**vars)
            else:
                value *= arg.eval(**vars)
        return value

    def diff(self, wrt):
        deriv = Constant(0)
        for i, arg in enumerate(self.args):
            term = arg.diff(wrt)
            for j, arg in enumerate(self.args):
                if j != i:
                    term *= arg
            if i == 0:
                deriv = term
            else:
                deriv += term
        return deriv

    def simplify(self):
        args = (a.simplify() for a in self.args)
        args = [a for a in args if a != 1]
        if len(args) > 1:
            return Mul(*args)
        elif len(args) == 1:
            return args[0]
        else:
            return Constant(1)


def express(object):
    if isinstance(object, Expression):
        return object
    elif isinstance(object, str):
        return Variable(object)
    else:
        return Constant(object)


if __name__ == '__main__':
    f = express('x')*'x'
    print(f)
    print(f.simplify())
    print(f.diff('x'))
    print(f.diff('x').simplify())

