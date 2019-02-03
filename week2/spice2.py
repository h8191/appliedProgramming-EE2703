import sys,cmath
import numpy as np

def valuate(x):
    '''converts string notation of magnitude to complex'''
    if isinstance(x,bool):  return int(x)
    if isinstance(x,str):
        orders ={'p':-12,'n':-9,'u':-6,'m':-3,'k':3,'M':6}
    if x[-1] in orders:
            return complex(x[:-1])*10**orders[x[-1]]
    return complex(eval(x))

def polarForm(x,polar=True):
    return (abs(x[0]),cmath.phase(x)*180/cmath.pi) if polar else x

class Element(object):
	allNodes = set()
	allBatteries = []
        controlledSouces = {i:[] for i in 'EFGH'}
    def __init__(self,info,freq):
        self.type = info[0][0]
        if self.type in 'RLCI':
            self.name, *self.nodes,value = info
            self.value = valuate(value)
        elif self.type == 'V':
        	Element.allBatteries.append(self)
            if info.pop(3)=='ac':
                self.name,*self.nodes,self.value,self.phase = info
                self.value, self.freq, self.phase = valuate(self.value)/2, freq,valuate(self.phase)
            else:
                self.name,*self.nodes,self.value = info
                self.value, self.freq, self.phase = valuate(self.value), 0, 0
        Element.allNodes.update(self.nodes)


    def admittance(self,W=0):
        if self.type == 'R':    return 1/self.value
        if self.type == 'C':    return 1j*W*self.value
        if self.type == 'L':    return -1j/(W*self.value)

    __str__ = lambda self: ' '.join('%s: %s'% item for item in vars(self).items())
        #', '.join([attr for attr in dir(self) if not attr.startswith()]
    isRLC = lambda self: self.type in 'RLC'

class Circuit(object):
    '''an object that solves dc resitive multiple Vsrcs,
         impedence circuit with one Voltage src(ac)'''
    def __init__(self,filename):
        self.readFile(filename)
        self.solve()
        self.printSolution(True)

    def readFile(self,filename):
        with open(filename,'r') as netlistFile:
            data = netlistFile.read().split('\n')
            CIRCUIT,END,AC = '.circuit','.end','.ac'
            Start,End,Ac = -1,-2,-3
            for line in data:
                if line[:len(CIRCUIT)] == CIRCUIT:
                    Start = data.index(line)
                if line[:len(END)] == END:
                    End = data.index(line)
                if line[:len(AC)] == AC:
                    Ac = data.index(line)
            self.w = valuate(Start<Ac<End and data[Ac].split()[-1])#short circuit and returning from boolean
            self.elements = [Element(line.split('#')[0].split(),self.w) for line in data[Start+1:End] if line[:len(AC)]!=AC]
            self.nodes = list(Element.allNodes)
            self.batteries = Element.batteries
            Element.allNodes, Element.allBatteries = set(),[]

    def solve(self):
        '''identify variables in x matrix'''
        self.variables = self.nodes + ['I'+i.name[1:] for i in self.batteries]#currents through batteries
        self.X = {i:[j,[]] for i,j in zip(self.variables,range(len(self.variables)))}
        #dict with nodes,keys = nodes,vSrcs vals[0] = indexes vals[1] = elements connected to load
        for element in self.elements:
            for node in element.nodes:
                self.X[node][1].append(element)
        
        self.rIndex,lenX = -1,len(self.X)
        self.A,self.b = np.zeros((lenX,lenX),dtype=np.complex64),np.zeros((lenX,1),dtype=np.complex64)

        #actual equations
        for node in self.nodes:
            self.nodalEquation(node,self.X[node][1])#kcl equations at each node
        for vSrc in self.batteries:
            self.voltageSrcEqn(vSrc)#potential difference between ends of battery Eqn

        self.solution = dict(zip(self.X,np.linalg.solve(self.A,self.b)))
        #with open('test.txt','a') as af:
            #af.write(str(self.X)+'\n'+str(self.solution.T)+'\n')

    def nodalEquation(self,node,connectedToThis):
        '''connectedToThis => list of all elements connected to this node'''
        constant = 0
        self.rIndex +=1
        if node in ('GND')#,'n0'):
            self.A[self.rIndex,self.X[node][0]] = 1 #V(GND) = 0
            return
        for element in connectedToThis:
            isFirstNode = node == element.nodes[0]# is node the first node of element
            if element.isRLC():
                otherNode = element.nodes[1] if isFirstNode else element.nodes[0]
                self.A[self.rIndex, self.X[node][0]] += element.admittance(self.w)
                self.A[self.rIndex, self.X[otherNode][0]] -= element.admittance(self.w)
            elif element.type == 'V':
                #assuming current flows in battery from node2 to node1
                self.A[self.rIndex, self.X['I'+element.name[1:]][0]] = -1 if isFirstNode else 1
            elif element.type=='I':
                #current flows from node 1 to node 2
                constant += (element.value if isFirstNode else -element.value)

        self.b[self.rIndex] = constant

    def voltageSrcEqn(self,vSrc):
        self.rIndex+=1
        self.A[self.rIndex, [self.X[vSrc.nodes[0]][0],self.X[vSrc.nodes[1]][0]]] = 1,-1# n1 - n2
        self.b[self.rIndex, 0] = vSrc.value*cmath.exp(vSrc.phase)# mag*exp(phase)

    def printSolution(self,polar=False,inOrder=True):
        if inOrder:
            print('\n'.join(('{} {}'.format(i,polarForm(self.solution[i],polar))
                     for i in sorted(self.variables))),end='\n\n')
            return
        
        print('\n'.join(('{} {}'.format(i,polarForm(j,polar))
                             for i,j in self.solution.items()),end='\n\n')) 

if __name__ == '__main__':
    circuits = [Circuit(filename) for filename in 
                            (sys.argv[1:] if len(sys.argv)>1 else input('enter filenames').split())]

