from pylab import *
from scipy.integrate import quad
from scipy.linalg import lstsq

fexp = np.exp
fcos = lambda x:np.cos(np.cos(x))

def FourierCoeffs(func=fcos,N=25):
    u,v = lambda x,k:func(x)*cos(k*x),lambda x,k:func(x)*sin(k*x)
    c = [quad(u,0,2*pi,0)[0]/(2*pi)]#pl
    for i in range(1,N+1):   c.extend([quad(u,0,2*pi,i)[0]/pi,quad(v,0,2*pi,i)[0]])
    return array(c).reshape(2*N+1,1)

N = 400
t=linspace(0,2*pi,N+1)[:-1].reshape(N,1)#column vector
#print(t)
A = np.ones(t.shape)
for i in range(1,26):
    A = hstack([A,cos(i*t),sin(i*t)])

t1 = np.linspace(-2*pi,4*pi,100,endpoint = False)
plt.figure(1)
plt.semilogy(t1,fexp(t1),label='fexp')
plt.legend();plt.grid(True)
plt.figure(2)
plt.plot(t1,fcos(t1),label='fcos')
plt.legend();plt.grid(True)

c1,c2 = FourierCoeffs(fexp), FourierCoeffs(fcos)

figure(3);semilogy();stem(arange(51),c1,label='fexp');grid(True)
figure(4);loglog();stem(arange(51),c1,label='fexp');legend();grid(True)
figure(5);semilogy();stem(arange(51),c2,label='fcos');grid(True)
figure(6);loglog();stem(arange(51),c2,label='fcos');legend();grid(True)

est1,est2 = lstsq(A,fexp(t))[0],lstsq(A,fcos(t))[0]

figure(3);semilogy();stem(arange(51),est1,'r',label='fexpEst');legend()
figure(5);semilogy();stem(arange(51),est2,'g',label='fcosEst');legend()

print("max diff in fexp {[0]},fcos {[0]}".format(max(abs(c1-est1)),max(abs(c2-est2))))
print(allclose(A.dot(est1),fexp(t),atol=1e3))

figure(7)
plot(t,fexp(t),label='fexp')
plot(t,A.dot(est1),label='fexpEst')
plot(t,A.dot(c1),label='fexpFcoeffs')
legend();grid(True)

figure(8)
plot(t,fcos(t),label='fcos')
plot(t,A.dot(est2),label='fcosEst')
plot(t,A.dot(c2),label='fcosFcoeffs')
legend();grid(True)

"""
figure(7)
plot(t,fexp(t),label='fexp')
plot(t,A.dot(est1),label='fexpEst')
plot(t,A.dot(c1),label='fexpFcoeffs')
legend();grid(True)

figure(8)
plot(t,fcos(t),label='fcos')
plot(t,A.dot(est2),label='fcosEst')
plot(t,A.dot(c2),label='fcosFcoeffs')
legend();grid(True)
"""
show()
