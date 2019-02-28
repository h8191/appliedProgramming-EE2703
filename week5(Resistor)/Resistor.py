import matplotlib.pyplot as plt
import numpy as np
import mpl_toolkits.mplot3d.axes3d as p3

Nx,Ny,radius,Niter = 25,25,8,1500
phi = np.zeros((Nx,Ny))
x,y = np.linspace(-12,12,Nx),np.linspace(12,-12,Ny)
X,Y = np.meshgrid(x,y)
ii = np.where(X*X+Y*Y<radius*radius)
phi[ii] = 1
print(X.shape,phi.shape)
errors = np.zeros(Niter)
for i in range(Niter):
	oldphi = phi.copy()
	phi[1:-1,1:-1] = (phi[1:-1,:-2]+phi[1:-1,2:]+phi[:-2,1:-1]+phi[2:,1:-1])/4
	phi[ii]=1
	phi[:,0],phi[:,-1]=phi[:,1],phi[:,-2]
	phi[0],phi[-1]=phi[1],0#phi[-2,:]
	errors[i] = np.max(np.abs(phi-oldphi))
	#phi[-1,:] = 1;phi[:,0],phi[0,:],phi[:,-1]=phi[:,1],0,phi[:,-2]
#plt.imshow(phi,cmap=plt.cm.hot,interpolation='bilinear');plt.figure()
#plt.contourf(X,Y,phi,cmap=plt.cm.hot)
X,Y = X+13,Y+13
plt.xlim([0,26])
plt.ylim([0,26])
Jx = (phi[1:-1,2:]-phi[1:-1,:-2])/2
Jy = (phi[2:,1:-1]-phi[:-2,1:-1])/2
Jx[-1],Jy[-1]=0,0

X1,Y1 = np.meshgrid(np.arange(1,24),np.arange(23,0,-1))#np.arange(24,0,-1))
plt.figure(1)
plt.title('Vector plot of The current flow')
plt.quiver(X1,Y1,Jx,Jy,scale=1/0.25)
plt.plot(ii[0],ii[1],'ro')

fig4 = plt.figure(4)
ax = p3.Axes3D(fig4)
plt.title('Surface potential')
#plt.zlabel('potential')
surface = ax.plot_surface(X,Y,phi,rstride=1,cstride=1,cmap=plt.cm.jet)

plt.xlim([0,26])
plt.ylim([0,26])

plt.figure(5)
plt.plot(errors)

plt.show()
print(errors)
