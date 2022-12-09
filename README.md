# Express

A simple python package for symbolic computation with support for automatic differentiation.

```python
from express import express, Tensor, Derivative

x1, x2, x3 = express('x1 x2 x3')
x = Tensor([x1, x2, x3])
print(x)

u1, u2, u3 = express('u1 u2 u3')
u = Tensor([u1, u2, u3])
print(u)

d1 = Derivative(x1)
d2 = Derivative(x2)
d3 = Derivative(x3)
D = Tensor([d1, d2, d3])
print(D)

print(D.inner(u))     # divergence
print(D.outer(u).T)   # gradient
print(D.inner(D) * u) # Laplacian
print(D.inner(D.outer(u).T))
```
```stdout
[x1 x2 x3]
[u1 u2 u3]
[d/dx1 d/dx2 d/dx3]
(du1/dx1 + du2/dx2 + du3/dx3)
[[du1/dx1 du1/dx2 du1/dx3]
 [du2/dx1 du2/dx2 du2/dx3]
 [du3/dx1 du3/dx2 du3/dx3]]
[((d/dx1 d/dx1) + (d/dx2 d/dx2) + (d/dx3 d/dx3))u1
 ((d/dx1 d/dx1) + (d/dx2 d/dx2) + (d/dx3 d/dx3))u2
 ((d/dx1 d/dx1) + (d/dx2 d/dx2) + (d/dx3 d/dx3))u3]
[((d/dx1 du1/dx1) + (d/dx2 du1/dx2) + (d/dx3 du1/dx3))
 ((d/dx1 du2/dx1) + (d/dx2 du2/dx2) + (d/dx3 du2/dx3))
 ((d/dx1 du3/dx1) + (d/dx2 du3/dx2) + (d/dx3 du3/dx3))]
```
