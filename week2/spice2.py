import sys,json
import numpy as np
import cmath
nonComment = lambda x: x.split('#',maxsplit=1)[0].split()
onePorts, twoPorts = list('RLCVI'),list('EFGH')

def valuate(x):
    return complex(eval(x))

class Element(object):
    def __init__(self,info,freq):
        self.type = info[0][0]
        if self.type in 'RLCI':
            self.name, *self.nodes,value = info
            self.value = valuate(value)
        elif self.type == 'V':
            if info.pop(3)=='ac':
                self.name,*self.nodes,self.value,self.phase = info
                self.value, self.freq, self.phase = int(self.value)/2, freq,valuate(self.phase)
            else:
                self.name,*self.nodes,self.value = info
                self.value, self.freq, self.phase = int(self.value), 0, 0
            #print(info)

    def admittance(self,W=0):
        if self.type == 'R':    return 1/self.value
        if self.type == 'C':    return 1j*W*self.value
        if self.type == 'L':    return 1/(1j*W*self.value)

    def __str__(self):
        return ' '.join('%s: %s'% item for item in vars(self).items())
        #', '.join([attr for attr in dir(self) if not attr.startswith()])
    isOnePort = lambda self: self.type in onePorts
    isRLC = lambda self: self.type in 'RLC'

class Circuit(object):
    def __init__(self,filename=None):
        self.readFile(filename)
        self.solve()

    def readFile(self,filename):
        with open(filename,'r') as netlistFile:
            data = netlistFile.read().split('\n')
            CIRCUIT,END,AC = '.circuit','.end','.ac'
            Start,End,self.w0,self.elements = -1,-1,0,[]
            for line in data:
                if line[:len(CIRCUIT)] == CIRCUIT:
                    Start = data.index(line)+1
                if line[:len(END)] == END:
                    End = data.index(line)
            for line in data[Start:End]:
                if line[:len(AC)] == AC:
                    self.w0 = 2*np.pi*int(line.split()[-1])
                else:
                    self.elements.append(Element(nonComment(line),self.w0))
        #print(data[Start:End])
        #print(self.elements)

    def solve(self):
        '''identify variables in x matrix'''
        self.currents = ['I'+i.name[1:] for i in self.elements if i.type == 'V']
        self.nodeList = {}# nodes as keys list of connected elements as values
        for element in self.elements:
            for node in element.nodes:
                if node in self.nodeList:
                    self.nodeList[node].append(element)
                else:
                    self.nodeList[node] = [element]
        self.X =  list(self.nodeList.keys()) + self.currents#list containing all unknowns
        self.rIndex = -1
        self.lenX = lenX = len(self.X)
        #print(lenX)
        self.A,self.b = np.zeros((lenX,lenX),dtype=np.complex64),np.zeros((lenX,1),dtype=np.complex64)
        [self.nodalEquation(node,self.nodeList[node]) for node in self.nodeList]
        [self.voltageSrcEqn(i) for i in self.elements if i.type=='V']
    
        
        self.solution = np.linalg.solve(self.A,self.b)
        print({i:j for i,j in zip(self.X,self.solution)})
        #with open('test.txt','a') as af:
            #af.write(str(self.X)+'\n'+str(self.solution.T)+'\n')

    def nodalEquation(self,node,connectedToThis):
        constant = 0
        self.rIndex +=1
        if node == 'GND':
            self.A[self.rIndex,self.X.index(node)] = 1 
            return 
        for element in connectedToThis:
            if element.isOnePort():
                isFirstNode = node == element.nodes[0]
                if element.isRLC():
                    otherNode = element.nodes[1] if isFirstNode else element.nodes[0]
                    #print(element.impedence(self.w0),print(element),self.w0)
                    self.A[self.rIndex, self.X.index(node)] += element.admittance(self.w0)
                    self.A[self.rIndex, self.X.index(otherNode)] -= element.admittance(self.w0)
                elif element.type == 'V':
                    #assuming current flows in battery from node2 to node1 terminal
                    self.A[self.rIndex, self.X.index('I'+element.name[1:])] = -1 if isFirstNode else 1
                elif element.type=='I':
                    #current flows from terminal 1 to terminal 2
                    constant += (element.value if isFirstNode else -element.value)
            self.b[self.rIndex] = constant

    def voltageSrcEqn(self,vSrc):
        self.rIndex+=1
        self.A[self.rIndex, [self.X.index(vSrc.nodes[0]),self.X.index(vSrc.nodes[1])]] = 1,-1
        self.b[self.rIndex, 0] = vSrc.value*cmath.exp(1j*self.w0+vSrc.phase)

    def dump(self):
        with open('log1.txt','w') as wf:
            json.dump(self,wf)


if __name__ == '__main__':
    ckt1 = Circuit('ckt4.netlist')
    #ckt2 = Circuit('ckt5.netlist')
