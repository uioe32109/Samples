from __future__ import print_function
import random, copy

class Grid:
	def __init__(self, problem):
		self.spots = [(i, j) for i in range(1,17) for j in range(1,17)]
		#print(self.spots)
		self.domains = {}
		#Need a dictionary that maps each spot to its related spots
		self.peers = {} 
		for i in range(1,17):
			for j in range(1,17):
				self.setup_peers((i,j),self.peers)
		self.parse(problem)
		#print(self.domains)
	def parse(self, problem):
		for i in range(0, 16):
			for j in range(0, 16):
				c = problem[i*16+j] 
				if c == '.':
					self.domains[(i+1, j+1)] = [0,1,2,3,4,5,6,7,8,9,17,18,19,20,21,22]
				else:
					self.domains[(i+1, j+1)] = [ord(c)-48]
	def display(self):
		for i in range(0, 16):
			for j in range(0, 16):
				d = self.domains[(i+1,j+1)]
				if len(d) == 1:
					print(chr(d[0]+48), end='')
				else: 
					print('.', end='')
				if j == 3 or j == 7 or j == 11:
					print(" | ", end='')
			print()
			if i == 3 or i == 7 or i == 11:
				print("-------------------------")

	def setup_peers(self, spot, peers):
		add_peers=[]
		# Column peers
		for i in range(1,17):
			if i == spot[0]:
				continue
			add_peers.append((i,spot[1]))
		# Row peers
		for j in range(1,17):
			if j == spot[1]:
				continue
			add_peers.append((spot[0],j))
		x = spot[0]
		y = spot[1]
		# A stupid way to add the square peer, 16 possible postions in a square, I just manually type them in.
		if x==1 or x==5 or x==9 or x==13:
			if y==1 or y==5 or y==9 or y==13:
				add_peers.extend([(x+1,y+1),(x+1,y+2),(x+1,y+3),(x+2,y+1),(x+2,y+2),(x+2,y+3),(x+3,y+1),(x+3,y+2),(x+3,y+3)])
			elif y==2 or y==6 or y==10 or y==14:
				add_peers.extend([(x+1,y-1),(x+2,y-1),(x+3,y-1),(x+1,y+1),(x+2,y+1),(x+3,y+1),(x+1,y+2),(x+2,y+2),(x+3,y+2)])
			elif y==3 or y==7 or y==11 or y==15:
				add_peers.extend([(x+1,y-2),(x+1,y-1),(x+1,y+1),(x+2,y-2),(x+2,y-1),(x+2,y+1),(x+3,y-2),(x+3,y-1),(x+3,y+1)])
			else:
				add_peers.extend([(x+1,y-3),(x+1,y-2),(x+1,y-1),(x+2,y-3),(x+2,y-2),(x+2,y-1),(x+3,y-3),(x+3,y-2),(x+3,y-1)])
		elif x==2 or x==6 or x==10 or x==14:
			if y==1 or y==5 or y==9 or y==13:
				add_peers.extend([(x-1,y+1),(x-1,y+2),(x-1,y+3),(x+1,y+1),(x+1,y+2),(x+1,y+3),(x+2,y+1),(x+2,y+2),(x+2,y+3)])
			elif y==2 or y==6 or y==10 or y==14:
				add_peers.extend([(x-1,y-1),(x-1,y+1),(x-1,y+2),(x+1,y-1),(x+1,y+1),(x+1,y+2),(x+2,y-1),(x+2,y+1),(x+2,y+2)])
			elif y==3 or y==7 or y==11 or y==15:
				add_peers.extend([(x-1,y-2),(x-1,y-1),(x-1,y+1),(x+1,y-2),(x+1,y-1),(x+1,y+1),(x+2,y-2),(x+2,y-1),(x+2,y+1)])
			else:
				add_peers.extend([(x-1,y-3),(x-1,y-2),(x-1,y-1),(x+1,y-3),(x+1,y-2),(x+1,y-1),(x+2,y-3),(x+2,y-2),(x+2,y-1)])
		elif x==3 or x==7 or x==11 or x==15:
			if y==1 or y==5 or y==9 or y==13:
				add_peers.extend([(x-2,y+1),(x-2,y+2),(x-2,y+3),(x-1,y+1),(x-1,y+2),(x-1,y+3),(x+1,y+1),(x+1,y+2),(x+1,y+3)])
			elif y==2 or y==6 or y==10 or y==14:
				add_peers.extend([(x-2,y-1),(x-2,y+1),(x-2,y+2),(x-1,y-1),(x-1,y+1),(x-1,y+2),(x+1,y-1),(x+1,y+1),(x+1,y+2)])
			elif y==3 or y==7 or y==11 or y==15:
				add_peers.extend([(x-2,y-2),(x-2,y-1),(x-2,y+1),(x-1,y-2),(x-1,y-1),(x-1,y+1),(x+1,y-2),(x+1,y-1),(x+1,y+1)])
			else:
				add_peers.extend([(x-2,y-3),(x-2,y-2),(x-2,y-1),(x-1,y-3),(x-1,y-2),(x-1,y-1),(x+1,y-3),(x+1,y-2),(x+1,y-1)])
		else:
			if y==1 or y==5 or y==9 or y==13:
				add_peers.extend([(x-3,y+1),(x-3,y+2),(x-3,y+3),(x-2,y+1),(x-2,y+2),(x-2,y+3),(x-1,y+1),(x-1,y+2),(x-1,y+3)])
			elif y==2 or y==6 or y==10 or y==14:
				add_peers.extend([(x-3,y-1),(x-3,y+1),(x-3,y+2),(x-2,y-1),(x-2,y+1),(x-2,y+2),(x-1,y-1),(x-1,y+1),(x-1,y+2)])
			elif y==3 or y==7 or y==11 or y==15:
				add_peers.extend([(x-3,y-2),(x-3,y-1),(x-3,y+1),(x-2,y-2),(x-2,y-1),(x-2,y+1),(x-1,y-2),(x-1,y-1),(x-1,y+1)])
			else:
				add_peers.extend([(x-3,y-3),(x-3,y-2),(x-3,y-1),(x-2,y-3),(x-2,y-2),(x-2,y-1),(x-1,y-3),(x-1,y-2),(x-1,y-1)])
		self.peers[spot] = add_peers

class Solver:
	def __init__(self, grid):
		#sigma is the assignment function
		self.sigma = copy.deepcopy(grid.domains)
		self.solution = {}
		self.grid = grid
		self.setup_domains(grid)
		# Initialize assignment
		for i in range(1,17):
			for j in range(1,17):
				if len(self.sigma[(i,j)])==1:
					self.solution[(i,j)] = self.sigma[(i,j)][0]
				else:
					self.solution[(i,j)] = -1
		#print(self.solution)

	# This function eliminate the impossible choices at the beginning for each unassigned spot
	def setup_domains(self, grid):
		for i in range(1,17):
			for j in range(1,17):
				if len(self.sigma[(i,j)])!=1:
					for k in grid.peers[(i,j)]:
						if len(self.sigma[(k[0],k[1])])==1:
							assignment = self.sigma[k[0],k[1]][0]
							if assignment in self.sigma[(i,j)]:
								#print("Index ",i,",",j, "remove option ", assignment)
								self.sigma[(i,j)].remove(assignment)

	def solve(self):
		result = True
		#Call backtrack algorithm
		result = self.backtrack()
		if result == False:
			return False
		else:
			return True

	def backtrack(self):
		# If assignment is complelte, return
		if self.check_complete(self.solution)==True:
			return True
		# Get a unassign spot
		unit = self.get_unassigned_spot(self.sigma)
		print(unit, " AVAILABLE CHOICE ",self.sigma[unit])
		# Check each possible choice
		for value in self.grid.domains[unit]:
			if value not in self.sigma[unit]:
				continue
			print("Check if ", unit, " can choose ", value)
			# If current choice is consistent, proceed and eliminate the domain for its peers.
			if self.consistent(unit, value, self.solution) == True:
				copy_solution = copy.deepcopy(self.solution)
				copy_sigma = copy.deepcopy(self.sigma)
				self.solution[unit] = value
				inference = self.infer(unit, value)
				# If inference is True, call backtrack
				if inference == True:
					print("Assign ", value, " to ", unit)
					self.sigma[unit] = [value]
					result = self.backtrack()
					# If future backtrack returns True, return True
					# Else some failure happens in the future due to the current choice, reset assignment
					if result == True:
						return result
					self.sigma = copy_sigma
					self.solution = copy_solution
				# If inference is False, current choice is not good
				else:
					print(unit, " reference return false at ", value)
					self.sigma = copy_sigma
					self.solution = copy_solution
			self.sigma[unit].remove(value)
			self.solution[unit] = (-1)
		print(unit, " fail to assign")
		return False

	# This function check if assigning the value to the spot will cause conflict
	def consistent(self, spot, value, solution):
		peer_list = self.grid.peers[spot]
		for (peerx, peery) in peer_list:
			index = (peerx,peery)
			if solution[index]!=(-1) and value == solution[index]:
				#print(spot, " conflicts with ", index, " at ", value)
				return False
		return True

	# Based on the choice for the spot, eliminate the domain for its peers and check for future decisions' result based on this choice
	def infer(self, spot, value):
		peer_list = self.grid.peers[spot]
		for i in peer_list:
			if self.solution[(i[0],i[1])]!=(-1):
				continue
			else:
				if value in self.sigma[(i[0],i[1])]:
					#print(value, " is removed from ",i)
					# Remove the choice from peer's domain
					self.sigma[(i[0],i[1])].remove(value)
					# If the peer ends up only having one choice, check it
					if len(self.sigma[(i[0],i[1])])==1:
						# If the one left choice for the peer is consistent for the current assignment, check for future decisions' based on this choice
						if self.consistent((i[0],i[1]), self.sigma[(i[0],i[1])][0], self.solution) == True:
							self.solution[(i[0],i[1])] = self.sigma[(i[0],i[1])][0]
							#print("Call infer on ", (i[0],i[1]), " by assiging it to ", self.sigma[(i[0],i[1])][0])
							result = self.infer((i[0],i[1]), self.sigma[(i[0],i[1])][0])
							if result == False:
								return False
							#print("Assign ", self.sigma[(i[0],i[1])][0], " to ", (i[0],i[1]))
						# Not consistent, all previous choices lead to this failure, redo previous decisions
						else:
							#print(spot, " can not be asigned ", value, " due to the conflict that causes by ", (i[0],i[1]))
							return False
					# The peer ends up with no choice, bad decision
					elif len(self.sigma[(i[0],i[1])])==0:
						#print(spot, "causes ",(i[0],i[1]), "to have no option")
						return False
					else:
						continue
		return True

	# This function check if the assignment is complete
	def check_complete(self, solution):
		for i in range(1,17):
			for j in range(1,17):
				if solution[(i,j)] == (-1):
					return False
		return True

	# This function return an unassigned spot, it will choose the one with the least amount of domain
	def get_unassigned_spot(self, sigma):
		domain_length = 17
		unassigned_spot = 0
		for (i,j) in sigma:
			if self.solution[(i,j)]==(-1):
				if len(sigma[(i,j)])<domain_length:
					unassigned_spot = (i,j)
					domain_length = len(sigma[(i,j)])
		return unassigned_spot

	# This function translate self.solution to the one that can be used for display()
	def tranverse_solution(self):
		return_solution = {}
		for i in range(1,17):
			for j in range(1,17):
				array = []
				array.append(self.solution[(i,j)])
				return_solution[(i,j)]=array
		return return_solution

easy = [".2......C....D8.6........F.8....5.C....B...2.......71.E..........8..9.2....7....10F.5...A3...8.......7.8..BEC9A...7.B.D42.9.E6F59.2.A..5.CD.8F...3..D......9...B7.1..BF.....65..EB...64.72..3.C.3C8..9.....41B..0DA..26C....74.E.........76F......B.F4..E0...AD9",
".2......C....D8.6........F.8....5.C....B...2.......71.E..........8..9.2....7....10F.5...A3...8.......7.8..BEC9A...7.B.D42.9.E6F59.2.A..5.CD.8F...3..D......9...B7.1..BF.....65..EB...64.72..3.C.3C8..9.....41B..0DA..26C....74.E.........76F......B.F4..E0...AD9",
"..1F....4.....3.E.6.3D.......0.90C.9.F..2.3D...B8.......7..E624....EB..D..4..8..5...E1A...7.3.2....A7.9.1..5..F..9F28.C6A...71...3....6.......8A..E...386..A....6....5BC3..8F.70....4..7FC0.E..6.4.C6.......0.....3.A..4.2..C5.....85...9..1....15..9.F2DB8....."]

hard = ["4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......",
"52...6.........7.13...........4..8..6......5...........418.........3..2...87....."]

# Solving a hexadoku takes time by using backtrack, need to wait for a bit.
# Even a easy one will take some wait time
print("====Problem====")
g = Grid(easy[1])
#Display the original problem
#print(g.peers[(6,6)])
g.display()
s = Solver(g)
if s.solve():
	print("====Solution===")
	#Display the solution
	#Feel free to call other functions to display
	g.domains = s.tranverse_solution()
	g.display()
else:
	print("==No solution==")

