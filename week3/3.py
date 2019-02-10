from pylab import *
from scipy.special import *
import scipy as sp
N,k = 101,9

g = lambda t,A,B: A*jn(2,t)+B*t
def msq(fk,t,A,B):
    """fk is row"""
    if fk.ndim == 1:
        fk = fk.reshape(len(fk),1)
    x = fk-g(t,A,B)
    return dot(x.T,x)[0][0]/len(t)
temp = loadtxt('fitting.dat')
t,yy = hsplit(temp,np.array([1]))#temp[:,0],temp[:,1:]
y = g(t,1.05,-0.105)
#1

plt.figure(0)
plt.xlabel(r'$t$ -->')
plt.ylabel(r'$f(t)+noise -->$')
plt.title('Q4:Data to be fitted to theory')
plot(t,yy)
plot(t,y,c='black')
legend([r'$\sigma_{}$'.format(i) for i in range(1,10)]+['True Value'])


#2
plt.figure(1)
tempy = loadtxt('fitting.dat',usecols=(1),unpack=True)
errorbar(t[::5],tempy[::5],0.1,fmt='ro',label='errorbar')
plot(t,y,label=r'$f(t)$')#g(t,1.05-0.105)
plt.xlabel(r'$t$ -->')
#plt.ylabel(r'$f(t)+noise -->$')
plt.title('Q5: Data Points for $\sigma$ = 0.10 along with exact function')
legend()
#show()

#6
A0,B0 = 1.05,-0.105
M = c_[jn(2,t),t]
p = c_[np.array([A0,B0])]#.reshape(2,1)
#print(M.shape,p.shape,dot(M,p).shape, g(t,A0,B0).shape)
#print(dot(M,p).shape == g(t,A0,B0).shape)
print(all(M.dot(p) == c_[g(t,A0,B0)]))#.reshape(t.shape[0],1))

#7 
print('#7 :')
for i,j in zip(linspace(0,2,21),linspace(-0.2,0,21)):
    print(msq(yy[:,0],t,0,j))


#8
X, Y = meshgrid(linspace(-5,5,11),linspace(-5,5,11)) 
#plt.clabel(plt.contour(X,Y,Z,color='red',linewidths=5,cmap='jet'),inline=1,fontsize=23)