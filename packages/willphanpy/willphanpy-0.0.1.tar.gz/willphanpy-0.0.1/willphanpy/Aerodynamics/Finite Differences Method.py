#import sympy
#import numpy
#import math
from numpy import *
from math import *
from sympy import *
import matplotlib.pyplot as plt

x = symbols('x')
#t = symbols('t')
u = sin(pi*x)
f = lambdify(x, u, "numpy")

X=[]
Y=[]

x = 0.25
#t = 0
dx = 0.25
dt = 0.25
for i in range(20):
    if x<=1:
        h = f(x) + (f(x+dx)-2*f(x)+f(x-dx))*dt/dx**2
        print(h)
        x = x + dx
        X.append(i)
        Y.append(h)
    else:
        break

plt.plot(X,Y)
plt.show()