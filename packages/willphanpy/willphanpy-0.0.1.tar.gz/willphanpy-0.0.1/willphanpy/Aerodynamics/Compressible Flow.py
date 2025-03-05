import sympy as sym
import numpy as np
import math
from sympy import*
from numpy import linspace
import matplotlib.pyplot as plt

# WHEN IS A FLOW CONSIDERED COMPRESSIBLE
x = symbols('x')
rho_0=1
gamma=1.4
rho = rho_0*(1+((gamma-1)*(x**2))/2)**(1/(1-gamma))
f=lambdify(x, rho, 'numpy')

x=linspace(0,5,100)
x1=linspace(0.3,0.3,100)
y1=linspace(0,1,100)
plt.plot(x,f(x))
plt.plot(x1,y1)
plt.show()