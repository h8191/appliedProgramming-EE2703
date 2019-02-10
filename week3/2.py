from pylab import *
from scipy.special import *
import scipy as sp
N,k = 101,9
A,B = 1.05,-0.105
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
"""
plt.figure(0)
plt.xlabel(r'$t\;\longrightarrow$')#\rightarrow
plt.ylabel(r'$f(t)+noise\;\longrightarrow$')
plt.title('Q4:Data to be fitted to theory')
#ax = axes()
#ax.arrow(3,5,6,7)
plot(t,yy)
plot(t,y,c='black')
legend([r'$\sigma_{}$'.format(i) for i in range(1,10)]+['True Value'])
"""
"""

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
"""
#6
"""
A0,B0 = 1.05,-0.105
M = c_[jn(2,t),t]
p = c_[np.array([A0,B0])]#.reshape(2,1)
#print(M.shape,p.shape,dot(M,p).shape, g(t,A0,B0).shape)
#print(dot(M,p).shape == g(t,A0,B0).shape)
print(all(M.dot(p) == c_[g(t,A0,B0)]))#.reshape(t.shape[0],1))
"""
"""
#6
A0,B0 = 1.05,-0.105
M = c_[jn(2,t),t]
p = np.array([[A0],[B0]])
#print(all(dot(M,p) == g(t,A0,B0)))#,M,p,g(t,A0,B0))
#print(msq(yy[:,0],t,1.05,-0.15))
"""
#7
""" 
print('#7 :')
for i,j in zip(linspace(0,2,21),linspace(-0.2,0,21)):
    print(msq(yy[:,0],t,0,j))
"""

#8
plt.figure(2)
X, Y = meshgrid(linspace(0,2,30),linspace(-0.2,0,30))
#Z = np.array([msq(yy[:,0],t,i,j) for i in linspace(0,2,30) for j in linspace(-0.2,0,30)]).reshape(X.shape)
Z =np.array([msq(yy[:,0],t,i,j) for i,j in zip(X.flatten('F'),Y.flatten('F'))]).reshape(X.shape)
scatter(A,B)
#print(Z)
#c = contour(X,Y,Z,20,linewidths=1,cmap='jet')

levels = [0.025*i if i<5 else 0.028*i for i in range(1,16)]
c = contour(X,Y,Z,levels,linewidths=1)#,cmap='jet'
plt.clabel(c,c.levels[:4],inline=1)

"""
#10
#bestAB = sp.linalg.lstsq(M,yy[:,0].reshape(len(t),1))
#print(bestAB)
#plt.figure(3)
sA,sB=[],[]
for i in range(9):
    bestAB = sp.linalg.lstsq(M,yy[:,i].reshape(len(t),1))[0]
    sA.append(bestAB[0][0]);sB.append(bestAB[1][0])
sA = abs(np.array(sA)-A)
sB = abs(np.array(sB)-B)
scl = logspace(-1,-3,k)
plot(scl,sA,'--o',c='red',label='Aerr')
plot(scl,sB,'--o',c='green',label='Berr')
title('Q10 Variation of error with noise')
xlabel(r'Noise standard deviation$\;\rightarrow$')
ylabel(r'MS error $\;\rightarrow$')
legend()
plt.figure(4)
loglog()
errorbar(scl,sA,yerr=scl,fmt='ro',label='Aerr')
errorbar(scl,sB,yerr=scl,fmt='go',label='Berr')
title('Q11 Variation of error with noise')
xlabel(r'$\sigma_{n}\;\longrightarrow$')
ylabel('MSerror$\;\rightarrow$')
legend()
"""
show()
