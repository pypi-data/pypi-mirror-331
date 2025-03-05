import numpy as np
from scipy.linalg import block_diag

# Two matrices are initialized by value
# Note that creating matrix in array of numpy library helps to identify rows and columns easily
#x = np.array([[1, 2], [4, 5]])
#y = np.array([[7, 8], [9, 10]])
#  add()is used to add matrices
#print ("Addition of two matrices: ")
#z = np.add(x,y)
#i = np.linalg.pinv(z) # make an inverse matrix
#print(i, k@np.eye(2)) # Note that @ is matrix multiplying (also use .dot())
#and * is multiply each element of A by a corresponding element of B
#print(i@z)

#print('z[0,1]: \n', z[0,1]) # '\n' means add a new line
#print('z[:,1]: \n', z[:,1])
#print('z[0,:]: \n', z[0,:])


#A = np.array([[-0.647,-0.493,0,0,0,0,0],
#              [0.507,-0.014,-0.493,0,0,0,0],
#              [0,0.507,-0.014,-0.493,0,0,0],
#              [0,0,0.507,201/3500,-0.493,0,0],
#              [0,0,0,0.507,-0.014,-0.493,0],
#              [0,0,0,0,0.507,-0.014,-0.493],
#              [0,0,0,0,0,1,-1]])
#b = np.array([0,0,0,0.01,0,0,0])
#x = np.linalg.solve(A, b)
#y = np.linalg.pinv(A)@b
#print(y)


N = 6
M = 2

pattern = np.array([[-1, 2, 4]])
upper = block_diag(*[pattern for i in range(N)])
lower = np.zeros((M, upper.shape[1]))
mat = np.vstack((upper, lower))
print(mat)

print([i for i in range(10) if i % 2 == 0])

X = np.loadtxt('univariate.txt', delimiter = ',')