import sys,os
#oneports, twoports = ['R','L','C','V','I'], ['E','F','G','H']
try:
    netlistFile = sys.argv[1]
except IndexError:
    netlistFile = input('please enter FileName: ')

netlistFile += '.netlist' if '.netlist' not in netlistFile else ''

if not os.path.isfile(netlistFile):    #if file does not exists
    print('The file "{}" does not exist in this folder.\
        \nselect one of the following: '.format(netlistFile))

    [print(i) for i in os.listdir(os.getcwd()) if '.netlist' in i]  
    netlistFile = input('enter correct Filename from above: ')

with open(netlistFile,'r') as rf:
    data = rf.read().split('\n')

circuitFound, elements, comments =False, [], {}

for i in data:
    if i[0]=='.':
        if i=='.circuit':
            circuitFound = True
            continue
        elif i=='.end':
            break
    if circuitFound:
        i1 = i.split('#')
        if len(i1)>1:   comments[i1[0].split()[0]] = i1[1]
        elements.append(i1[0].split())

for i in elements[::-1]:
    print(' '.join(i[::-1]))
