import numpy as np
import sympy as sym
import math 
import scipy
import matplotlib.pyplot as plt

M = float(input('Enter Mach number: '))
the = input('Enter Deflection Angle: ')
theta = float(float(the)*math.pi/180)
y = float(input('Enter the heat capacity ratio: '))
x = sym.symbols('x')
z = sym.symbols('z')

g = sym.atan(2*(M**2*(sym.sin(x))**2-1)/(sym.tan(x)*(M**2*(y + sym.cos(2*x))+2)))
h = sym.lambdify(x, g - theta, 'numpy')
dx = 1e-10
fd = sym.diff(g)
fd = sym.lambdify(x , fd, 'numpy')

tol = 1e-10
xn = 20*math.pi/180
for n in range(100):
    xnew=xn-h(xn)/fd(xn)
    if abs(xnew - xn)<tol:
        break
    print(xnew)
    xn=xnew
print('The Wave Angle is: ',xn*180/math.pi)

# Calculate the pressure ratio
ratio = 1 + (2*y/(y+1))*(M**2*math.sin(xn)**2 - 1)
rho_ratio = ((y+1)*M**2*math.sin(xn)**2)/(2+(y-1)*M**2*math.sin(xn)**2)

print('The pressure ratio between upstream and downstream: ',ratio)
print('The temperature ratio between upstream and downstream: ',ratio*rho_ratio**(-1))
# g = sym.atan(2*(z**2*(sym.sin(x))**2-1)/(sym.tan(x)*(z**2*(y + sym.cos(2*x))+2)))
# f = sym.lambdify([x,z], g*180/math.pi, 'numpy')
# degree = np.linspace(0.01 ,90, 1000)
# radian = degree*math.pi/180
# plt.plot(f(radian,1.2), degree,f(radian,1.5), degree,f(radian,2), degree,f(radian,2.5), degree)
# plt.plot(f(radian,3), degree, f(radian,3.5), degree, f(radian,4), degree, f(radian,4.5), degree, f(radian,5), degree)
# plt.title(''r'$\beta$ - 'r'$\theta$ - M Relation')
# plt.xlabel('Deflection Angle 'r'$\theta$')
# plt.ylabel('Wave Angle 'r'$\beta$')
# plt.legend(['1.2','1.5','2','2.5','3','3.5','4','4.5','5'])
# plt.show()