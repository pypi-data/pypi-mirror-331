import numpy as np
import sympy as sym
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import LinearSegmentedColormap
#Plotting
#M_1 = np.linspace(1, 10, 100)
#M_12 = np.linspace(0, 1, 100)
#plt.plot(M_1,g(M_1), 'r', M_12, u(M_12), 'b')
#plt.title()
#plt.xlabel('Mach')
#plt.ylabel('Ratio p_02/p_1')
#plt.legend(['Supersonic','Subsonic']) 
#plt.savefig('o.png')
#plt.show()

fig = plt.figure()
a = fig.add_subplot(111)
u = np.linspace(-2,2,1000)
v = np.linspace(-2,2,1000)
x, y = np.meshgrid(u,v)
z = x**2 + y**2
#c = a.contourf(x,y,z)
#c = plt.imshow(z)
#plt.clabel(c, inline=1, fontsize = 10,)
plt.imshow(z, cmap=plt.cm.get_cmap('Reds', 6))
plt.colorbar(orientation='horizontal')
#plt.clim(-1, 20);
plt.axis('equal')
plt.show()


data = np.random.randint(10, size=(100, 100))
an_image = plt.imshow(data)
plt.colorbar(an_image)
plt.show()