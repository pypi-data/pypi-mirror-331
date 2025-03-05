import matplotlib.pyplot as plt
import numpy as np  
import math
import sympy as sym
from sympy import *
  
#NACA 4-DIGIT
Series=input('Enter a NACA series: ')
y_mc=int(Series[0])/100
x_mc=int(Series[1])/10
t_m=int(Series[2:4])/100
print('The maximum camber is', y_mc,'c')
print('Its location is ',x_mc,'c')
print('The maximum thickness is',t_m,'c')

x = sym.symbols('x') 

dx=1e-10
Xu=[]
Yu=[]
Xl=[]
Yl=[]

y_c_l =(y_mc)*(2*(x/x_mc)-(x/x_mc)**2)
y_c_r =(y_mc)*(2*((1-x)/(1-x_mc))-((1-x)/(1-x_mc))**2)
y_c_ll = sym.lambdify(x, y_c_l,"numpy")
y_c_rr = sym.lambdify(x, y_c_r,"numpy")
t = t_m*(2.969*sqrt(x)-1.260*x-3.516*x**2+2.843*x**3-1.0515*x**4)
slope_c_l = (y_c_ll(x+dx)-y_c_ll(x))/dx
slope_c_r = (y_c_rr(x+dx)-y_c_rr(x))/dx

x_i=0
for i in range(100):
    if x_i<x_mc:
        y_c=y_c_l
        slope_c=slope_c_l
    else:
        y_c=y_c_r
        slope_c=slope_c_r

    x_u = lambdify(x, x-(t/(2*(1+(slope_c)**2)**(0.5)))*slope_c, "numpy")
    y_u = lambdify(x,y_c+(t/(2*(1+(slope_c)**2)**(0.5))),"numpy")
    x_l = lambdify(x, x+(t/(2*(1+(slope_c)**2)**(0.5)))*slope_c,"numpy")
    y_l = lambdify(x,y_c-(t/(2*(1+(slope_c)**2)**(0.5))),"numpy")
    
    print(x_u(x_i))
    print(x_l(x_i))
    print(y_u(x_i))
    print(y_l(x_i))

    Xu.append(x_u(x_i))
    Yu.append(y_u(x_i))
    Xl.append(x_l(x_i))   
    Yl.append(y_l(x_i))
    x_i = x_i + 0.01

plt.plot(Xu,Yu)
plt.plot(Xl,Yl)
plt.title('NACA Airfoil')
plt.xlabel('x')
plt.ylabel('y')
plt.axis('equal')
plt.legend(['Upper surface','Lower surface'])
plt.show()

# import pandas as pd
# X = Xu + Xl
# Y = Yu + Yl
# df = pd.DataFrame(X)
# df.to_excel(excel_writer = "C:/Users/DELL/Desktop/X.xlsx")
# df = pd.DataFrame(Y)
# df.to_excel(excel_writer = "C:/Users/DELL/Desktop/Y.xlsx")