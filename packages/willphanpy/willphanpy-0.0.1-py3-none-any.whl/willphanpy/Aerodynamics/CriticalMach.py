import sympy as sym
import numpy as np
import math
y = 1.4
Cp0 = -0.43
x = sym.symbols('x')
Cpcr = (2/(y*x**2))*(((1+0.5*(y-1)*x**2)/(1+0.5*(y-1)))**(y/(y-1))-1)
Cp = Cp0/(1-x**2)**0.5
f = Cpcr - Cp
f = sym.lambdify(x, f, 'numpy')
dx = 1e-10
fd = (f(x+dx)-f(x-dx))/(2*dx)
fd = sym.lambdify(x, fd, 'numpy')
tol = 1e-4
xo = 0.99
for i in range(100):
    xn = xo - f(xo)/fd(xo)
    if abs(xn - xo) < tol:
        break
    else:
        xo = xn
print('Critical Mach Number:' ,xn)

