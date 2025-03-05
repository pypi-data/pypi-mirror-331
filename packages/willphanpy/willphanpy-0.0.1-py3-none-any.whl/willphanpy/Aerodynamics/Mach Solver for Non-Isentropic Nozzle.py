import sympy as sym
import numpy as np
import math
import matplotlib.pyplot as plt

p_pito = 0.5*101325
p_o = 10*101325
p_a = 0
T_o = 2000
T_e = 488.4
A_o = 0.3
A_e = 23.256
y = 1.2
R = 287
# # Mass flow
# m = p_o*A_o*((y/(T_o*R))*(2/(y+1))**((y+1)/(y-1)))**0.5
# # Mach when knowing T_o and T_e
# M_e = ((2/(y-1))*(T_o/T_e-1))**0.5
# # Total pressure when knowing M_e and p_e
# p_oe = p_e*(1+0.5*(y-1)*M_e**2)**(y/(y-1))

# Define x
x = sym.symbols('x')

# The first assumption is when the nozzle is isentropic
# Solving for Exit Mach number
# h = (1/x)*((2/(y+1))*(1+0.5*(y-1)*x**2))**(0.5*(y+1)/(y-1))
# f = sym.lambdify(x, h - A_e/A_o, 'numpy')
# dx = 0.001
# fd = (f(x+dx)-f(x-dx))/(2*dx)
# fd = sym.lambdify(x, fd, 'numpy')
# xo = 6
# tol = 1e-6
# for i in range(100):
#     xn = xo - f(xo)/fd(xo)
#     if abs(xn - xo)<tol:
#         break
#     else:
#         xo = xn
# print('M1: ',xn)

# p_e = p_o*((1+0.5*(y-1)*xn**2)**(y/(1-y)))

# M_2 = ((1+(y-1)*x**2/2)/(y*x**2-(y-1)/2))**(0.5)
# p_0_2_over_p_2 = (1+((y-1)*M_2**2)/2)**(y/(y-1))
# p_2_over_p_1 = 1+(2*y*(x**2-1)/(y+1))
# k = p_0_2_over_p_2*p_2_over_p_1
# f = sym.lambdify(x, k - p_pito/p_e, 'numpy')
# dx = 0.001
# fd = (f(x+dx)-f(x-dx))/(2*dx)
# fd = sym.lambdify(x, fd, 'numpy')
# xo = 6
# tol = 1e-6
# for i in range(100):
#     xn = xo - f(xo)/fd(xo)
#     if abs(xn - xo)<tol:
#         break
#     else:
#         xo = xn
# print('M1: ',xn)

# The second assumption is when the nozzle is not isentropic
A_eo = p_o*A_o/p_pito
# Solving for Exit Mach number
h = (1/x)*((2/(y+1))*(1+0.5*(y-1)*x**2))**(0.5*(y+1)/(y-1))
f = sym.lambdify(x, h - A_e/A_eo, 'numpy')
dx = 0.001
fd = (f(x+dx)-f(x-dx))/(2*dx)
fd = sym.lambdify(x, fd, 'numpy')
xo = 6
tol = 1e-6
for i in range(100):
    xn = xo - f(xo)/fd(xo)
    if abs(xn - xo)<tol:
        break
    else:
        xo = xn
print('Exit Mach Number: ', xn)
M_e = xn

# Exit Pressure
p_e = p_pito/((1+0.5*(y-1)*M_e**2)**(y/(y-1)))
print('Exit Pressure: ', p_e/101325,'atm')
# Exit Temperature
T_e = T_o/(1+0.5*(y-1)*M_e**2)
print('Exit Temperature: ', T_e,'K')
# Mass flow
m = p_o*A_o*((y/(T_o*R))*(2/(y+1))**((y+1)/(y-1)))**0.5
print('Mass flow: ', m,'Kg/s')
u_e = M_e*(y*R*T_e)**0.5
print('u_e: ',u_e)
F = m*u_e + (p_e - p_a)*A_e # N
print('Thrust of the Nozzle: ', F,'N')

# Equation for solving Exit Mach number when shock wave standing inside the nozzle
f = ((1+0.5*(y-1)*x**2)**(y/(1-y)))*((1/x)*((2/(y+1))*(1+0.5*(y-1)*x**2))**(0.5*(y+1)/(y-1))) - (p_e*A_e)/(p_o*A_o)
f = sym.lambdify(x, f, 'numpy')
dx = 0.001
fd = (f(x+dx)-f(x-dx))/(2*dx)
fd = sym.lambdify(x, fd, 'numpy')
xo = 6
tol = 1e-6
for i in range(100):
    xn = xo - f(xo)/fd(xo)
    if abs(xn - xo)<tol:
        break
    else:
        xo = xn
print('Exit Mach Number: ', xn)

# # Equation for solving Mach number before the shock wave standing inside the nozzle
# M_2 = (1+0.5*(y-1)*x**2)/(y*x**2-0.5*(y-1))
# p_02_2 = (1+0.5*(y-1)*M_2)**(y/(y-1))
# p_01_1 = (1+0.5*(y-1)*x**2)**(y/(1-y))
# p_2_1 = 1+(2*y/(y+1))*(x**2-1)
# f = p_02_2*p_01_1*p_2_1 - p_oe/p_o
# f = sym.lambdify(x, f, 'numpy')
# dx = 0.001
# fd = (f(x+dx)-f(x-dx))/(2*dx)
# fd = sym.lambdify(x, fd, 'numpy')
# #print(f(1.97))
# xo = 3
# tol = 1e-6
# for i in range(100):
#     xn = xo - f(xo)/fd(xo)
#     if abs(xn - xo)<tol:
#         break
#     else:
#         xo = xn
# print('M1: ',xn)