import numpy as np
import sys
import cmath

class component:
      def __init__(self,bn,edn,value):
              self.bn=bn;
              self.edn=edn;
              self.value=value;
q=0;
p=0;
set1=[]
x=0;y=0;
G=[];B=[];C=[];D=[];E=[];
circuit='.circuit'
End='.end'
with open(argv[1]) as f:
     lines=f.readlines()            
     for line in lines:
       if circuit==line[:len(circuit)]:
              start=lines.index(line)
       elif End==line[:line(End)]:
              end=lines.index(line)
              break

     if start>=end:
        print('invalid circuit')

        exit()

for a in (start+1:end):
             l[a]=line[a].split('#')[0].split()()
for c in (start+1:end):
          

for b in (start+1:end):
      l0=l[b].split()
         if l0[0]=='R'
                l1=l0[1].split(n)
                if l1[0]=='G'
                        .x=0;
                else
                   x=float(l1[0])
                l2=l0[2].split(n)
                if l2[0]=='G'
                        y=0; 
                else
                    y=float(l2[0])
                v=float(l0[3])
                if x>0 and y>0:
                 G[x-1][y-1]=-1/v
                 G[y-1][x-1]=-1/v
                if x>0:
                 G[x-1][x-1]+=1/v
                if y>0   :    
                 G[y-1][y-1]+=1/v
         elif l0[0]=='V':
              vl1=l0[1].split(n)
              if vl1[0]=='G'
                        x=0;
              else
                   x=float(vl1[0])
              vl2=l0[2].split(n)
              if l2[0]=='G'
                        y=0; 
              else
                    y=float(vl2[0])
              v=float(l0[3]) 
              if x>0 :         
                 B[p][x-1]=1  
                 C[x-1][p]=1
              if  y>0:
                 B[p][y-1]=-1
                 C[y-1][p]=-1 
              E[p]=v
              p+=1
         elif  l0[0]='I':  
              v=float(l0[3])
              I[q]=v
              q+=1








