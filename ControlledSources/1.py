import sys,cmath,numpy as np

nonComment = lambda line:line.split('#')[0].split()

def myRound(x,ndigits=6):
    return '{0.real:0.{2}f} {1} {0.imag:0.{2}f}j'.format(x, '' if x.imag<0 else '+',ndigits)

def Eval(x):
    '''converts string notation of magnitude to complex'''
    if isinstance(x,str) and x[-1] in 'pnumkM':
        return complex(x[:-1])*10**dict(zip('pnumkM',(-12,-9,-6,-3,3,6)))[x[-1]]
    return eval(x)

def polarForm(x,polar=True,ndigits=6):
    #return (abs(x),cmath.phase(x)*180/cmath.pi) if polar else x
    if polar:   return '{:0.6f}, {:0.6f}'.format(abs(x),cmath.phase(x)*180/cmath.pi)
    return myRound(x,ndigits)

class Element(object):
    Nodes = set()
    RLC = []
    V,I = [],[]
    E,H = [],[]#VCVS,CCVS
    F,G = [],[]#CCCS,VCCS
    ACSources = {}
    def __init__(self,info):
        self.type = info[0][0]
        valid = False
        if self.type in tuple('RLC') and len(info)==4:
            self.value,self.name,*self.nodes,valid = Eval(info.pop()),*info,True

        elif self.type in tuple('VI'):
            if info[3] == 'ac' and len(info)==6:       
                self.phase,self.value,self.name,*self.nodes,self._type = Eval(info.pop()),Eval(info.pop())/2,*info
                Element.ACSources[self.name] = self;valid = True
            elif info[3] == 'dc' and len(info)==5:
                self.phase,self.value,self.name,*self.nodes,self._type = 0,Eval(info.pop()),*info
                self.freq = 0;valid = True

        elif self.type in tuple('EG') and len(info)==6:
            self.name,self.nodes,self.inNodes,self.gain,valid = Eval(info[0]),info[1:3],info[3:5],Eval(info[5]),True
            Element.Nodes.update(self.inNodes)

        elif self.type in tuple('FH') and len(info)==5:
            self.gain,self.name,*self.nodes,self.input,valid = info.pop(),*info,True
            
        if not valid:   raise Exception

        if self.type in tuple('VEH'):   self.current = 'I({})'.format(self.name)
        if self.type in tuple('RLC'):   Element.RLC.append(self)
        if self.type in tuple('VIEFGH'):    eval('Element.{}'.format(self.type)).append(self)

        Element.Nodes.update(self.nodes)#update exists only for sets

    def admittance(self,W=0):
            if self.type == 'R':    return 1/self.value
            if self.type == 'C':    return 1j*W*self.value
            if self.type == 'L':    return -1j/(W*self.value)

    _value = lambda self: self.value if self._type=='dc' else cmath.rect(self.value,self.phase*cmath.pi/180)# mul == div left to right

    def _clearClassVariables():
        Element.Nodes,Element.ACSources = set(),{}
        for i in ['RLC']+list('VIEFGH'):
            exec("Element."+i+" = []")#exec("eval(Element.{}'.format(i)) = []")

    __str__ = lambda self: ' '.join('%s: %s'% item for item in vars(self).items())
        #', '.join([attr for attr in dir(self) if not attr.startswith()]

class Circuit(object):
    def __init__(self,filename):
        Element._clearClassVariables()
        self.w = 0
        # input for phase in 
        self.ReadFile(filename)
        self.SolveCircuit()
        self.PrintSolution()

    def ReadFile(self,filename):
        try:
            with open(filename,'r') as netlistFile:
                data = netlistFile.read().split('\n')
        except(FileNotFoundError,IOError):
            print('invalid filename: file not found');quit()
        
        CIRCUIT,END,AC = '.circuit','.end','.ac'
        Start,End = -1,-2
        for line in data:
            if line[:len(CIRCUIT)] == CIRCUIT:
                Start = data.index(line)
            if line[:len(END)] == END:
                End = data.index(line)

        self.ParseData(data[Start+1:End],data[End+1:])

    def ParseData(self,data,freqData):
        for line in data:  Element(nonComment(line))
        #extract data from Element class variables
        self.nodes = list(Element.Nodes)
        for i in ['RLC','ACSources']+list('VIEFGH'):#copying data from elements to self
            exec("self."+i+" = Element."+i)#eval('self.{}'.format(i)) = eval('Element.{}'.format(i))
            pass
        variables = self.nodes + [i.current for i in (self.V+self.E+self.H)]
        self.vars = dict(zip(variables,range(len(variables))))

        for line in map(nonComment,freqData):
            if len(line)==3 and line[0] == '.ac':
                self.ACSources[line[1]].freq = Eval(line[2])
                self.w = 2*np.pi*Eval(line[2])

    def SolveCircuit(self):
        '''identify variables in x matrix'''
        lenX = len(self.vars)
        print(self.vars)
        A,B = np.zeros((lenX,lenX),dtype=np.complex64),np.zeros((lenX,1),dtype=np.complex64)
        for e in self.RLC:
            A[self.vars[e.nodes[0]],self.vars[e.nodes[0]]] += e.admittance(self.w)
            A[self.vars[e.nodes[0]],self.vars[e.nodes[1]]] -= e.admittance(self.w)
            A[self.vars[e.nodes[1]],self.vars[e.nodes[0]]] -= e.admittance(self.w)
            A[self.vars[e.nodes[1]],self.vars[e.nodes[1]]] += e.admittance(self.w)
        
        for e in self.V+self.E+self.H:
            #assume current is flowing out from +ve/first node
            A[self.vars[e.nodes[0]],self.vars[e.current]] -= 1#nodal equation
            A[self.vars[e.nodes[1]],self.vars[e.current]] += 1#nodal equation
            A[self.vars[e.current],self.vars[e.nodes[0]]] = 1#volatge diff equation
            A[self.vars[e.current],self.vars[e.nodes[1]]] = -1#volatge diff equation
            if e.type=='V':  B[self.vars[e.current],0] = e._value()#volatge diff equation
            if e.type=='E':#v1 - v2 = v3 -v4 => v1 -v2 -v3 +v4 =0
                A[self.vars[e.current], self.vars[e.inNodes[0]]] -= e.gain
                A[self.vars[e.current], self.vars[e.inNodes[1]]] += e.gain
            if e.type=='H':#v1 -v2 -HI() = 0
                A[self.vars[e.current],self.vars['I({})'.format(e.input)]] = -e.gain

        for e in self.I:
            #assume current is flowing out from +ve/first node(from node2 to node1)
            B[self.vars[e.nodes[0]],0] += e._value()#since goes to constant matrix
            B[self.vars[e.nodes[1]],0] -= e._value()
        #VSources = {i.name:i for i in self.V}
        for e in self.G:# i = G(V3-V4)
            A[self.vars[e.nodes[0]],self.vars[e.inNodes[0]]] -= e.gain#-v3
            A[self.vars[e.nodes[0]],self.vars[e.inNodes[1]]] += e.gain#+v4
            A[self.vars[e.nodes[1]],self.vars[e.inNodes[0]]] -= e.gain#+v3
            A[self.vars[e.nodes[1]],self.vars[e.inNodes[1]]] += e.gain#-v4
        for e in self.F:
            A[self.vars[e.nodes[0]],self.vars['I({})'.format(e.input)]] -= e.gain
            A[self.vars[e.nodes[1]],self.vars['I({})'.format(e.input)]] += e.gain
        A[self.vars['GND'],:], B[self.vars['GND'],0] = 0,0#overwriting GND equation
        A[self.vars['GND'],self.vars['GND']] = 1

        solution = np.linalg.solve(A,B).reshape(lenX)
        self.solution = dict(zip(self.vars,solution))
        self.A,self.B = A,B

    def PrintSolution(self,fileObj=sys.stdout):
        print('the answer approximated to 6 decimal places is:')
        print('\n'.join(('{0}\t{1}'.format(i,myRound(self.solution[i]))
                    for i in sorted(self.vars))),end='\n\n',file=fileObj)
        
if __name__ == '__main__':
    if len(sys.argv)>1:
        ckts = [Circuit(i) for i in sys.argv[1:]]
        # this code can take multiple netlist files and solve them in one command line
    else:
        print('Please (proper) filename and try again')
