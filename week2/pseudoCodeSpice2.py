import numpy as np

class Component(object):
	def __init__(self,*args):
		#initialize with whatever you want
		pass
	def impedence(self,frequency):
		# returns impedence of RLC in ac circuit
		pass

class Circuit:
	def __init__(self,filename):
		self.readFile(filename)
		self.solve()
		self.printSolution()

	def readFile(self,filename):
		'''
		read a file and store all elements as Component
		in self.Components
		'''
		pass
	def solve(self):
	 	pass 
	 	'''
	 	create a dict/list to store all the elements in
	 	the netlist file
	 	a list to store all the variables v at nodes
	 	and i through batteries
	 	'''
	 	"""
	 	n = len(list of variables)
	 	self.A => (nxn) ;self.b => (nx1)
	 	for node in nodes:
	 		nodalEquation(node)
	 	for battery in batteries:
	 		batteryEquation(battery)
	 	"""

	def nodalEquation(self,node):
		#for i in components connected to the node
		#	if impedence
		#		do something
		#	if volatgesource
		# 		"do something else"
		pass

	def batteryEqn(self):
		#V(firstnode) - V(secondnode) = V(battery)
		pass
