import sympy as sym
import numpy as np
import math
import matplotlib.pyplot as plt

Z = np.genfromtxt('Nozzle_Z.txt', delimiter = ',')
X = np.genfromtxt('Nozzle_X.txt', delimiter = ',')

y = 1.22
p_o = 20.4 #Mpa
T_o = 3500 #°K
p_e = 16.8727 #KPa
R = 287 #J/Kg.K
ga = 9.80665 #m/s2

ratio = Z[len(Z)-1]**2/min(Z)**2
x = sym.symbols('x')
g = (1/x)*((2/(y+1))*(1+0.5*(y-1)*x**2))**(0.5*(y+1)/(y-1))
f = sym.lambdify(x, g - ratio, 'numpy')
dx = 0.001
fd = (f(x+dx)-f(x-dx))/(2*dx)
fd = sym.lambdify(x, fd, 'numpy')
# Newton Iteration
tol = 1e-6
x_o = 4
for i in range(1000):
    x_n = x_o - f(x_o)/fd(x_o)
    if abs(x_o - x_n) < tol:
        break
    else:
        #print(x_o)
        x_o = x_n

p_exit = p_o*(1+0.5*(y-1)*x_n**2)**(y/(1-y))*1e3
T_e = T_o*(1+0.5*(y-1)*x_n**2)**(-1)
print('Mach number at the exit: ',x_n)
print('Pressure at the exit: ', p_exit, 'KPa')
print('Temperature at the exit: ', T_e, '°K')

# Plot Mach number versus x
x = sym.symbols('x')
r_o = min(Z)
Ratio = Z**2/r_o**2
M = []
for i in range(len(Z)):
    h = g - Ratio[i]
    f = sym.lambdify(x, h, 'numpy')
    dx = 0.001
    fd = (f(x+dx)-f(x-dx))/(2*dx)
    fd = sym.lambdify(x, fd, 'numpy')
    # Newton Iteration
    if X[i] < X[list(Z).index(min(Z))]:
        x_o = 0.1
    else:
        x_o = 4
    tol = 1e-6
    for j in range(100):
        x_n = x_o - np.array(f(x_o))/np.array(fd(x_o))
        if abs(x_o - x_n) < tol:
            break
        else:
            x_o = x_n
    M.append(x_n)

# Plot pressure and temperature versus x
p = sym.lambdify(x, p_o*(1+0.5*(y-1)*x**2)**(y/(1-y))*1e3, 'numpy')
T = sym.lambdify(x, T_o*(1+0.5*(y-1)*x**2)**(-1), 'numpy')
print('Pressure at the throat: ', p(1))
print('Temperature at the throat: ', T(1))

# Solve for Thrust and ISP in vacuum
A_o = math.pi*r_o**2*1e-4
A_e = math.pi*max(Z)**2*1e-4
m = (p_o*1e6)*A_o*((y/(T_o*R))*(2/(y+1))**((y+1)/(y-1)))**0.5
u_e = float(M[len(Z)-1])*(y*R*T_e)**0.5
p_a = 0 #Vacuum
F = m*u_e + (p_exit - p_a)*A_e # N
ISP = F/(m*ga) # s
print('Thrust of the Nozzle in vacuum: ',F,'N')
print('Thrust in lbf: ',F/4.4482216153,' lbf')
print('ISP in vacuum: ',ISP,'s')

# Plotting
plt.plot(X, M)
plt.title('Mach number variation along the SSME Nozzle')
plt.xlabel('x')
plt.ylabel('Mach')
plt.show()
plt.plot(X, p(np.array(M)))
plt.title('Pressure distribution along the SSME Nozzle')
plt.xlabel('x')
plt.ylabel('p')
plt.show()
plt.plot(X, T(np.array(M)))
plt.title('Temperature distribution along the SSME Nozzle')
plt.xlabel('x')
plt.ylabel('T')
plt.show()

