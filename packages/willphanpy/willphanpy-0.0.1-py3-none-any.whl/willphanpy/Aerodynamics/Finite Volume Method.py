import numpy as np
import sympy as sym
import math
import matplotlib.pyplot as plt

# initial Input
k = 0.6 # W/(mK)
rho = 1e3 # kg/m3
Cp = 4181 # J/kgK
umax = 0.01 # m/s
xcell = 50
ycell = 20
dx = 100e-6/xcell
dy = 20e-6/ycell
TWs = 200
TWw = 450
TWn = 300

# Define variables
T, Tw, Tn, Te, Ts, y, u = sym.symbols('T, Tw, Tn, Te, Ts, y, u')

#Define velocity function
h = umax*(1-(2*y/20e-6)**2)
h = sym.lambdify(y,h,'numpy')

# Define discretized equations
# Because we have 4 boundaries. 4 corners, and 1 center => we got 9 equations below
U = (k/dx)*((Te - T)/dx - (T - Tw)/dx) + (k/dy)*((Tn - T)/dy - (T - Ts)/dy) - (rho*Cp*u/dx)*((Te + T)/2 - (T + Tw)/2) #1
W = (k/dx)*((Te - T)/dx - (T - Tw)/(0.5*dx)) + (k/dy)*((Tn - T)/dy - (T - Ts)/dy) - (rho*Cp*u/dx)*((Te + T)/2 - Tw) #2
S = (k/dx)*((Te - T)/dx - (T - Tw)/dx) + (k/dy)*((Tn - T)/dy - (T - Ts)/(0.5*dy)) - (rho*Cp*u/dx)*((Te + T)/2 - (T + Tw)/2) #3
N = (k/dx)*((Te - T)/dx - (T - Tw)/dx) + (k/dy)*((Tn - T)/(0.5*dy) - (T - Ts)/dy) - (rho*Cp*u/dx)*((Te + T)/2 - (T + Tw)/2) #4
E = -(k/dx)*((T - Tw)/dx) - (rho*Cp*u/dx)*(T - (T+Tw)/2) +(k/dy)*(Tn - T)/dy - (k/dy)*(T-Ts)/dy

SW = S + W - U #6
NW = N + W - U #7
SE = -(k/dx)*((T - Tw)/dx) - (rho*Cp*u/dx)*(T - (T+Tw)/2) + k*(Tn - T)/dy - k*(T-Ts)/(dy/2) #8
NE = -(k/dx)*((T - Tw)/dx) - (rho*Cp*u/dx)*(T - (T+Tw)/2) + k*(Tn - T)/(dy/2) - k*(T-Ts)/dy #9

# Create a coefficient matrix, a free coefficient matrix, a Velocity matrix
A = np.zeros((xcell*ycell,xcell*ycell))
b = np.zeros((xcell*ycell,1))

u_ma = np.zeros((xcell*ycell,1))
for i in range(ycell):
    for j in range(xcell*i,xcell+xcell*i):
        u_ma[j] = h(-ycell*dy/2 + dy/2 + dy*i)

# Identify the order of each cell
sw = 0
se = xcell-1
nw = xcell*(ycell-1)
ne = xcell*ycell-1
# For cell 1 from the southewest
f = sym.lambdify([T, Tw, Tn, Te, Ts, u], SW, 'numpy')
A[sw,sw]=f(1,0,0,0,0, u_ma[sw])
A[sw,sw+1]=f(0,0,0,1,0,u_ma[sw])
A[sw,sw+xcell]=f(0,0,1,0,0,u_ma[sw])
b[sw]= -f(0,TWw,0,0,TWs,u_ma[sw])
# For cell 50 from the southeast
f = sym.lambdify([T, Tw, Tn, Te, Ts, u], SE, 'numpy')
A[se,se]=f(1,0,0,0,0,u_ma[se])
A[se,se-1]=f(0,1,0,0,0,u_ma[se])
A[se,se+xcell]=f(0,0,1,0,0,u_ma[se])
b[se]= -f(0,0,0,0,TWs,u_ma[se])
# For cell 50*19+1 from the northwest
f = sym.lambdify([T, Tw, Tn, Te, Ts, u], NW, 'numpy')
A[nw,nw]=f(1,0,0,0,0,u_ma[nw])
A[nw,nw+1]=f(0,0,0,1,0,u_ma[nw])
A[nw,nw-xcell]=f(0,0,0,0,1,u_ma[nw])
b[nw]= -f(0,TWw,TWn,0,0,u_ma[nw])
# For cell 50*20 from the northeast
f = sym.lambdify([T, Tw, Tn, Te, Ts, u], NE, 'numpy')
A[ne,ne]=f(1,0,0,0,0,u_ma[ne])
A[ne,ne-1]=f(0,1,0,0,0,u_ma[ne])
A[ne,ne-xcell]=f(0,0,0,0,1,u_ma[ne])
b[ne]= -f(0,0,TWn,0,0,u_ma[ne])
# For cell from 2 to 50-1 from the south
f = sym.lambdify([T, Tw, Tn, Te, Ts, u], S, 'numpy')
list_s= list(range(1,xcell-1))
for i, j in zip(list_s,list_s):
    A[i,j-1]=f(0,1,0,0,0,u_ma[i])
    A[i, j] =f(1,0,0,0,0,u_ma[i])
    A[i,j+1]=f(0,0,0,1,0,u_ma[i])
    A[i,j+xcell]=f(0,0,1,0,0,u_ma[i])
    b[i]= -f(0,0,0,0,TWs,u_ma[i])
# For cell from 1+50j (j=1,18) from the west
f = sym.lambdify([T, Tw, Tn, Te, Ts, u], W, 'numpy')
list_w = [i for i in range(1,xcell*ycell-xcell) if i % xcell == 0]
for i, j in zip(list_w, list_w):
    A[i,j]=f(1,0,0,0,0,u_ma[i])
    A[i,j+1]=f(0,0,0,1,0,u_ma[i])
    A[i,j+xcell]=f(0,0,1,0,0,u_ma[i])
    A[i,j-xcell]=f(0,0,0,0,1,u_ma[i])
    b[i]= -f(0,TWw,0,0,0,u_ma[i])
# For cell 50+50*j (j=1,18) from the east
f = sym.lambdify([T, Tw, Tn, Te, Ts, u], E, 'numpy')
list_e = np.array([i for i in range(2*xcell,xcell*ycell) if i % xcell == 0]) - 1
for i, j in zip(list_e, list_e):
    A[i,j]=f(1,0,0,0,0,u_ma[i])
    A[i,j-1]=f(0,1,0,0,0,u_ma[i])
    A[i,j+xcell]=f(0,0,1,0,0,u_ma[i])
    A[i,j-xcell]=f(0,0,0,0,1,u_ma[i])
    b[i]= -f(0,0,0,0,0,u_ma[i])
# For cell from 1+50*19 to 50*20 from the north
f = sym.lambdify([T, Tw, Tn, Te, Ts, u], N, 'numpy')
list_n = list(range(xcell*(ycell-1)+1,xcell*ycell-1))
for i, j in zip(list_n, list_n):
    A[i,j]=f(1,0,0,0,0,u_ma[i])
    A[i,j-1]=f(0,1,0,0,0,u_ma[i])
    A[i,j+1]=f(0,0,0,1,0,u_ma[i])
    A[i,j-xcell]=f(0,0,0,0,1,u_ma[i])
    b[i]= -f(0,0,TWn,0,0,u_ma[i])
# For the entire cells excluding the cells along the boundary
list = list(range(xcell*ycell))
for i in [sw,se,nw,ne]:
    list.remove(i)
for e in list_w:
    if e in list:
        list.remove(e)
for e in list_s:
    if e in list:
        list.remove(e)
for e in list_n:
    if e in list:
        list.remove(e)
for e in list_e:
    if e in list:
        list.remove(e)

f = sym.lambdify([T, Tw, Tn, Te, Ts, u], U, 'numpy')
for i, j in zip(list, list):
    A[i,j]=f(1,0,0,0,0,u_ma[i])
    A[i,j-1]=f(0,1,0,0,0,u_ma[i])
    A[i,j+1]=f(0,0,0,1,0,u_ma[i])
    A[i,j+xcell]=f(0,0,1,0,0,u_ma[i])
    A[i,j-xcell]=f(0,0,0,0,1,u_ma[i])
    b[i]= -f(0,0,0,0,0,u_ma[i])

# Solve the linear equation AX=b
X = np.linalg.pinv(A)@b
#print(X)

# Rearrange X(1000x1) to Y(20x50) 
Y = np.zeros((ycell,xcell))
L = [i for i in range(ycell)]
L.reverse()
for i in L:
    for j in range(xcell):
        Y[i,j] = X[xcell*(ycell-1-i)+j]
print('Y',Y)

# Rearrange Velocity matrix (1000x1) to (20x50)
V = np.zeros((ycell,xcell))
L = [i for i in range(ycell)]
L.reverse()
for i in L:
    for j in range(xcell):
        V[i,j] = u_ma[xcell*(ycell-1-i)+j]
#print('V',V)

# Plotting contour
an_image = plt.imshow(Y)#, cmap=plt.cm.get_cmap('Greens', 1000))
plt.colorbar(an_image, shrink = 1.25, orientation = 'horizontal')
plt.show()
#an_image1 = plt.imshow(V)#, cmap=plt.cm.get_cmap('Greens', 1000))
#plt.colorbar(an_image1, shrink = 1.25, orientation = 'horizontal')
#plt.show()


# Plot temperature along the centerline versus x
X = []
for i in range(xcell):
    X.append(0.5*dx + dx*i)
T = []
for j in range(xcell):
    y_center = int(0.5*ycell)
    T.append(Y[y_center, j])

plt.plot(X, T, 'b')
plt.title('Temperature distribution along the centerline')
plt.xlabel('x')
plt.ylabel('T_centerline')
plt.show()

# Export to xlsx file
#import pandas as pd
#df = pd.DataFrame(Y)
#df.to_excel(excel_writer = "C:/Users/DELL/Desktop/Temperature Distribution.xlsx")