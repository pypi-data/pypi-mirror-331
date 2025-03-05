import sympy as sym
x = 6.6
y = 1.4
p_oe = 0.8
p_o = 12
A_e = 80*0.4
A_o = 0.4
T_o = 2500
R = 287

m = p_o*101325*A_o*((y/(T_o*R))*(2/(y+1))**((y+1)/(y-1)))**0.5
print(m)
# x = sym.symbols('x')
# f = (1/x)*((2/(y+1))*(1+0.5*(y-1)*x**2))**(0.5*(y+1)/(y-1))
# f = sym.lambdify(x, f - 80*0.4/6, 'numpy')
# dx = 0.001
# fd = (f(x+dx)-f(x-dx))/(2*dx)
# fd = sym.lambdify(x, fd, 'numpy')
# xo = 0.01
# tol = 1e-6
# for i in range(100):
#     xn = xo - f(xo)/fd(xo)
#     if abs(xn - xo)<tol:
#         break
#     else:
#         xo = xn
# print('Exit Mach Number: ', xn)

# M_e = 0.11
# p_e = p_pito/((1+0.5*(y-1)*M_e**2)**(y/(y-1)))
# print(p_e)
# T = T_o/(1+0.5*(y-1)*M_e**2)
# print(T)

# x = 12
# M_2 = ((1+(y-1)*x**2/2)/(y*x**2-(y-1)/2))**(0.5)
# p_0_2_over_p_2 = (1+((y-1)*M_2**2)/2)**(y/(y-1))
# p_2_over_p_1 = 1+(2*y*(x**2-1)/(y+1))
# h = p_0_2_over_p_2*p_2_over_p_1
# print(h)

# f = ((1+0.5*(y-1)*x**2)**(y/(1-y)))*((1/x)*((2/(y+1))*(1+0.5*(y-1)*x**2))**(0.5*(y+1)/(y-1))) - (p_e*A_e)/(p_o*A_o)
# f = sym.lambdify(x, f, 'numpy')
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
# print('Exit Mach Number: ', xn)

x = sym.symbols('x')
M_2 = (1+0.5*(y-1)*x**2)/(y*x**2-0.5*(y-1))
p_02_2 = (1+0.5*(y-1)*M_2)**(y/(y-1))
p_01_1 = (1+0.5*(y-1)*x**2)**(y/(1-y))
p_2_1 = 1+(2*y/(y+1))*(x**2-1)
f = p_02_2*p_01_1*p_2_1 - p_oe/p_o
f = sym.lambdify(x, f, 'numpy')
dx = 0.001
fd = (f(x+dx)-f(x-dx))/(2*dx)
fd = sym.lambdify(x, fd, 'numpy')
#print(f(1.97))
xo = 3
tol = 1e-6
for i in range(100):
    xn = xo - f(xo)/fd(xo)
    if abs(xn - xo)<tol:
        break
    else:
        xo = xn
print('M1: ',xn)

x = 4.9
M_2 = ((1+(y-1)*x**2/2)/(y*x**2-(y-1)/2))**(0.5)
print(M_2)

f = A_o*(1/x)*((2/(y+1))*(1+0.5*(y-1)*x**2))**(0.5*(y+1)/(y-1))
print(f)