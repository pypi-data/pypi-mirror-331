# Calculation of CL and CD for flat plate over compressible flow (M>1)
import numpy as np
import sympy as sym
import math 
import scipy
import matplotlib.pyplot as plt

Mach = input('Enter Mach number: ')
Gamma = input('Enter gamma: ')
aoa = input('Enter the angle of attack: ')
y = float(Gamma)
M0 = float(Mach)
a = float(aoa)*math.pi/180

# Calculate the downstream Mach number
x = sym.symbols('x')
g = ((x**2-1)**(0.5))/((1+((y-1)/2)*x**2)*x)
h = sym.lambdify(x, g, 'numpy')

dM = 0.005  #increment
f = 0
M = M0
for i in range(1000):
    df = (((h(M+dM)+h(M))/2)*dM)
    f = f + df
    if f > abs(a):
        break
    else:
        M = M + dM
        #print('M:', M)

# Calcualate the Wave Angle
g = sym.atan(2*(M0**2*(sym.sin(x))**2-1)/(sym.tan(x)*(M0**2*(y + sym.cos(2*x))+2)))
h = sym.lambdify(x, g - abs(a), 'numpy')
fd = sym.diff(g)
fd = sym.lambdify(x , fd, 'numpy')

tol = 1e-10
xn = 20*math.pi/180
for n in range(100):
    xnew=xn-h(xn)/fd(xn)
    if abs(xnew - xn)<tol:
        break
    #print(xnew)
    xn=xnew

# Calculate pu_over_p1 and pl_over_p1
pu_over_p1 = ((1+(y-1)*M0**2/2)/(1+(y-1)*M**2/2))**(y/(y-1))
pl_over_p1 = 1+(2*y/(y+1))*(M0**2*sym.sin(xn)**2-1)
# Calculate the lift and drag coefficiens
cn = (2/(y*M0**2))*(pl_over_p1 - pu_over_p1)
# Because there is no friction, then the axial force is zero that means ca = 0
cd = cn*math.sin(a)
cl = cn*math.cos(a)
if a >= 0:
    print('The downstream Mach number over the upper surface is: ',M)
    print('The Wave Angle at the lower surface is: ',xn*180/math.pi)
    print('Lift coefficien is', cl)
    print('Drag coeeficien is', cd)
else:
    print('The downstream Mach number over the lower surface is: ',M)
    print('The Wave Angle at the upper surface is: ',xn*180/math.pi)
    print('Lift coefficien is', -cl)
    print('Drag coeeficien is', -cd)
