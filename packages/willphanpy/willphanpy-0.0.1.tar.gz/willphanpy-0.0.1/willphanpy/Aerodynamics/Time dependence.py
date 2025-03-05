import sympy as sym
import numpy as np
import math
import matplotlib.pyplot as plt

# Constant value
k = 205 #W/mK
Cp = 910 #J/kgK
rho = 2700 #Kg/m3
L = 0.1 #m
t = 0.4
dx = 0.002 #m
dt = 0.01 #s
T_wo = 373 #K
T_eo = 323 #KT
T_o = 0

T_new, T_old, T_w, T_e = sym.symbols('T_new, T_old, T_w, T_e')
f = Cp*rho*(T_new - T_old)/dt - (k/dx)*((T_e - T_old)/dx - (T_old - T_w)/dx)
l = Cp*rho*(T_new - T_old)/dt - (k/dx)*((T_e - T_old)/dx - 2*(T_old - T_w)/dx)
r = Cp*rho*(T_new - T_old)/dt - (k/dx)*(2*(T_e - T_old)/dx - (T_old - T_w)/dx)
f = sym.lambdify([T_new, T_old, T_w, T_e], f, 'numpy')
l = sym.lambdify([T_new, T_old, T_w, T_e], l, 'numpy')
r = sym.lambdify([T_new, T_old, T_w, T_e], r, 'numpy')

n = int(L/dx)
m = int(t/dt)+1
T = np.zeros((m,n))
for i in range(n):
    T[0,i] = T_o
#print(T)
for i in range(1,m):
    t = i*dt
    print(t)
    T[i,0] = -l(0,T[i-1,0],T_wo,T[i-1,1])/l(1,0,0,0)
    for j in range(1,4):
        T[i,j] = -f(0,T[i-1,j],T[i-1,j-1],T[i-1,j+1])/f(1,0,0,0)
    T[i,n-1] = -r(0,T[i-1,4],T[i-1,3],T_eo)/r(1,0,0,0)
print(T)

T_final = []
for i in range(n):
    T_final.append(T[m-1,i])

X = np.linspace(0.5*dx,L-dx,n)
plt.plot(X, T_final)
plt.show()