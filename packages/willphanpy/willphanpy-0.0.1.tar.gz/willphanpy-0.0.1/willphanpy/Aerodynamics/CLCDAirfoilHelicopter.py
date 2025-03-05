import numpy as np
import sympy as sym
import math

# Max Headspeed
MHS = 2550 # RPM #Max Headspeed
# Wings diameter
d = 790e-3 #m
# Airfoil NACA 0012 - Symmetric Airfoil
# Pitch ranging from 11 to 13 degrees
# Density
rho = 1.225 #Kg/m3
# Viscosity
muy = 1.789e-5 #Kg/ms
# Chord
c = 34e-3 #m

# Determine wingstep for one airfoil which has a uniform velocity under the same angular velocity
# Reynolds number

# Lift coefficient
Cl = 0.884
# dL = 0.5*rho*V**2*Cl*dr*c
# but V = omega*r
x = sym.symbols('x')
f = (0.5*rho*Cl*c*(2*math.pi*MHS/60)**2)*x**2
f = sym.lambdify(x, f, 'numpy')

n = 100
dr = d/(2*n)
r = 0
L = 0
for i in range(100):
    dL = 0.5*(f(r+dr)+f(r))*dr
    L += dL
    if r+dr==d/2:
        break
    else:
        r += dr
print('Lift: ', 1000*2*L/9.8067)