

class Expression(object):

    def __init__(self, *args):
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

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return 'Constant({})'.format(repr(self.value))

    def eval(self, **vars):
        return self.value

    def diff(self, wrt):
        return Constant(0)


class Variable(Expression):

    def __init__(self, name):
        self.name = str(name)

    def __repr__(self):
        return 'Variable({})'.format(repr(self.name))

    def __eq__(self, other):
        return isinstance(other, Variable) and self.name == other.name

    def eval(self, **vars):
        return vars.get(self.name, self)

    def diff(self, wrt):
        return Constant(1) if wrt == self else Constant(0)


class Add(Expression):

    def __init__(self, *args):
        self.args = [express(a) for a in args]

    def __repr__(self):
        return 'Add({})'.format(', '.join(repr(a) for a in self.args))

    def eval(self, **vars):
        sum = 0
        for arg in self.args:
            sum += arg.eval(**vars)
        return sum

    def diff(self, wrt):
        sum = Constant(0)
        for arg in self.args:
            sum += arg.diff(wrt)
        return sum


class Mul(Expression):

    def __init__(self, *args):
        self.args = [express(a) for a in args]

    def __repr__(self):
        return 'Mul({})'.format(', '.join(repr(a) for a in self.args))

    def eval(self, **vars):
        prod = 1
        for arg in self.args:
            prod *= arg.eval(**vars)
        return prod

    def diff(self, wrt):
        sum = Constant(0)
        for i, arg1 in enumerate(self.args):
            prod = 1
            for j, arg2 in enumerate(self.args):
                if i == j:
                    prod *= arg2.diff(wrt)
                else:
                    prod *= arg2
            sum += prod
        return sum


def express(obj):
    if isinstance(obj, Expression):
        return obj
    elif isinstance(obj, str):
        return Variable(obj)
    else:
        return Constant(obj)


if __name__ == '__main__':
    x = express('x')
    y = express('y')
    f = x*y
    print(f)
    print(f.diff(wrt=x))
