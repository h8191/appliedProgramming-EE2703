import sys,cmath
import numpy as np

nonComment = lambda line:line.split('#')[0].split()
#myRound = lambda x: '{0.real:0.6f} {1} {0.imag:0.6f}j'.format(x,'-' if x.imag<0 else '+')
def myRound(x,ndigits=6):
    return '{0.real:0.{2}f} {1} {0.imag:0.{2}f}j'.format(x, '' if x.imag<0 else '+',ndigits)
def valuate(x):
    '''converts string notation of magnitude to complex'''
    if isinstance(x,bool):  return int(x)
    if isinstance(x,str) and x[-1] in 'pnumkM':
        return complex(x[:-1])*10**dict(zip('pnumkM',(-12,-9,-6,-3,3,6)))[x[-1]]
    return complex(eval(x))

def polarForm(x,polar=True,ndigits=6):
    #return (abs(x),cmath.phase(x)*180/cmath.pi) if polar else x
    if polar:
        return '{:0.6f}, {:0.6f}'.format(abs(x),cmath.phase(x)*180/cmath.pi)
    return myRound(x,ndigits)

class Element(object):
    Nodes = set()
    RLCs = []
    Batteries = []
    CSources = []
    def __init__(self,info):
        self.type = info[0][0]
        if self.type in 'RLC':
            self.name,*self.nodes,value = info
            self.value = valuate(value)
        elif self.type in 'VI':
            if info[3] == 'ac':
                self.name,*self.nodes, self._type, value,phase = info
                self.value,self.phase = valuate(value)/2,valuate(phase)
            elif info[3] == 'dc':
                self.name,*self.nodes, self._type, value = info
                self.value,self.phase,self.freq = valuate(value),0,0
             
            if self.type == 'V':    Element.Batteries.append(self);self.current = 'I'+self.name[1:]
            if self.type == 'I':    Element.CSources.append(self)

        Element.Nodes.update(self.nodes)

    def admittance(self,W=0):
        if self.type == 'R':    return 1/self.value
        if self.type == 'C':    return 1j*W*self.value
        if self.type == 'L':    return -1j/(W*self.value)

    def _clearClassVariables():
    	Element.Nodes,Element.Batteries,Element.RLCs = set(),[],[]

    __str__ = lambda self: ' '.join('%s: %s'% item for item in vars(self).items())
        #', '.join([attr for attr in dir(self) if not attr.startswith()]
    isRLC = lambda self: self.type in 'RLC'

class Circuit(object):
    def __init__(self,filename):
        self.w = 0
        self.ReadFile(filename)
        self.SolveCircuit()
        self.PrintSolution(polar = False)

    def ReadFile(self,filename):
        with open(filename,'r') as netlistFile:
            data = netlistFile.read().split('\n')
            CIRCUIT,END,AC = '.circuit','.end','.ac'
            Start,End = -1,-2
            for line in data:
                if line[:len(CIRCUIT)] == CIRCUIT:
                    Start = data.index(line)
                if line[:len(END)] == END:
                    End = data.index(line)

            self.elements = [Element(nonComment(line)) for line in data[Start+1:End]]
            self.nodes = list(Element.Nodes)
            self.batteries = Element.Batteries
            self.cSources = Element.CSources
            variables = self.nodes + [i.current for i in self.batteries]
            self.vars = dict(zip(variables,range(len(variables))))

            for line in data[End+1:]:
                line = nonComment(line)
                if len(line)>0 and line[0] == '.ac':
                    for element in {'I':self.cSources,'V':self.batteries}[line[1][0]]:
                        if element.name == line[1]:
                            element.freq = valuate(line[2])
                            self.w = 2*np.pi*valuate(line[2])

            Element._clearClassVariables()

    def SolveCircuit(self):
        '''identify variables in x matrix'''
        lenX = len(self.vars)
        A,B = np.zeros((lenX,lenX),dtype=np.complex64),np.zeros((lenX,1),dtype=np.complex64)
        for e in self.elements:
            if e.isRLC():
                A[self.vars[e.nodes[0]],self.vars[e.nodes[0]]] += e.admittance(self.w)
                A[self.vars[e.nodes[0]],self.vars[e.nodes[1]]] -= e.admittance(self.w)
                A[self.vars[e.nodes[1]],self.vars[e.nodes[0]]] -= e.admittance(self.w)
                A[self.vars[e.nodes[1]],self.vars[e.nodes[1]]] += e.admittance(self.w)
            if e.type == 'V':
                #assume current is flowing out from +ve/first node
                A[self.vars[e.nodes[0]],self.vars[e.current]] = -1
                A[self.vars[e.nodes[1]],self.vars[e.current]] = 1
                A[self.vars[e.current],self.vars[e.nodes[0]]] = 1
                A[self.vars[e.current],self.vars[e.nodes[1]]] = -1
                B[self.vars[e.current],0] = e.value*cmath.exp(1j*e.phase)
            if e.type == 'I':
                #assume current is flowing out from +ve/first node
                current  = e.value*cmath.exp(1j*e.phase)
                B[self.vars[e.nodes[0]],0] = -current
                B[self.vars[e.nodes[1]],0] = +current
        
        A[self.vars['GND'],:], B[self.vars['GND'],0] = 0,0#overwriting GND equation
        #A[:,self.vars['GND']] = 0
        A[self.vars['GND'],self.vars['GND']] = 1

        solution = np.linalg.solve(A,B).reshape(lenX)
        self.solution = dict(zip(self.vars,solution))
        self.A,self.B = A,B

    def PrintSolution(self,polar=False,fileObj=sys.stdout):
        print('\n'.join(('{0} {1}'.format(i,polarForm(self.solution[i],polar))
                    for i in sorted(self.vars))),end='\n\n',file=fileObj)
        return
        
if __name__ == '__main__':
    circuits = [Circuit(filename) for filename in 
                            (sys.argv[1:] if len(sys.argv)>1 else input('enter filenames').split())]
