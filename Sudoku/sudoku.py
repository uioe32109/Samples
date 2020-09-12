from __future__ import print_function
import random, copy
import subprocess
import time

class Grid:
	def __init__(self, problem):
		self.spots = [(i, j) for i in range(1,10) for j in range(1,10)]
		self.domains = {}
		#Need a dictionary that maps each spot to its related spots
		self.peers = {} 
		for i in range(1,10):
			for j in range(1,10):
				self.setup_peers((i,j),self.peers)
		self.parse(problem)
	def parse(self, problem):
		for i in range(0, 9):
			for j in range(0, 9):
				c = problem[i*9+j] 
				if c == '.':
					self.domains[(i+1, j+1)] = list(range(1,10))
				else:
					self.domains[(i+1, j+1)] = [ord(c)-48]
	def display(self):
		for i in range(0, 9):
			for j in range(0, 9):
				d = self.domains[(i+1,j+1)]
				if len(d) == 1:
					print(d[0], end='')
				else: 
					print('.', end='')
				if j == 2 or j == 5:
					print(" | ", end='')
			print()
			if i == 2 or i == 5:
				print("---------------")

	def setup_peers(self, spot, peers):
		add_peers=[]
		# Column peers
		for i in range(1,10):
			if i == spot[0]:
				continue
			add_peers.append((i,spot[1]))
		# Row peers
		for j in range(1,10):
			if j == spot[1]:
				continue
			add_peers.append((spot[0],j))
		x = spot[0]
		y = spot[1]
		# Square peers, 9 possible positions
		if x%3==1 and y%3==1:
			#print("(",x,",",y,")")
			add_peers.extend([(x+1,y+1),(x+2,y+1),(x+1,y+2),(x+2,y+2)])
		elif x%3==2 and y%3==1:
			#print("(",x,",",y,")")
			add_peers.extend([(x-1,y+1),(x-1,y+2),(x+1,y+1),(x+1,y+2)])
		elif x%3==0 and y%3==1:
			#print("(",x,",",y,")")
			add_peers.extend([(x-2,y+1),(x-1,y+1),(x-2,y+2),(x-1,y+2)])
		elif x%3==1 and y%3==2:
			#print("(",x,",",y,")")
			add_peers.extend([(x+1,y-1),(x+2,y-1),(x+1,y+1),(x+2,y+1)])
		elif x%3==2 and y%3==2:
			#print("(",x,",",y,")")
			add_peers.extend([(x-1,y-1),(x+1,y-1),(x-1,y+1),(x+1,y+1)])
		elif x%3==0 and y%3==2:
			#print("(",x,",",y,")")
			add_peers.extend([(x-2,y-1),(x-1,y-1),(x-2,y+1),(x-1,y+1)])
		elif x%3==1 and y%3==0:
			#print("(",x,",",y,")")
			add_peers.extend([(x+1,y-2),(x+2,y-2),(x+1,y-1),(x+2,y-1)])
		elif x%3==2 and y%3==0:
			#print("(",x,",",y,")")
			add_peers.extend([(x-1,y-2),(x-1,y-1),(x+1,y-2),(x+1,y-1)])
		else:
			#print("(",x,",",y,")")
			add_peers.extend([(x-2,y-2),(x-2,y-1),(x-1,y-2),(x-1,y-1)])
		peers[spot] = add_peers



class Solver:
	def __init__(self, grid):
		#sigma is the assignment function
		self.sigma = copy.deepcopy(grid.domains)
		self.solution = {}
		self.grid = grid
		self.setup_domains(grid)
		# Initialize assignment
		for i in range(1,10):
			for j in range(1,10):
				if len(self.sigma[(i,j)])==1:
					self.solution[(i,j)] = self.sigma[(i,j)][0]
				else:
					self.solution[(i,j)] = 0
		#for (i,j) in self.solution:
			#if self.solution[(i,j)]==0:
				#print("(",i,", ", j, "): ",self.sigma[(i,j)])

	# This function eliminate the impossible choices at the beginning for each unassigned spot
	def setup_domains(self, grid):
		for i in range(1,10):
			for j in range(1,10):
				if len(self.sigma[(i,j)])!=1:
					for k in grid.peers[(i,j)]:
						if len(self.sigma[k])==1:
							assignment = self.sigma[k][0]
							if assignment in self.sigma[(i,j)]:
								#print("Index ",i,",",j, "remove option ", assignment)
								self.sigma[(i,j)].remove(assignment)

	def solve(self):
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
		#print(unit, " AVAILABLE CHOICE ",self.sigma[unit])
		# Check each possible choice
		for value in self.grid.domains[unit]:
			if value not in self.sigma[unit]:
				continue
			#print("Check if ", unit, " can choose ", value)
			# If current choice is consistent, proceed and eliminate the domain for its peers.
			if self.consistent(unit, value, self.solution) == True:
				copy_solution = copy.deepcopy(self.solution)
				copy_sigma = copy.deepcopy(self.sigma)
				self.solution[unit] = value
				inference = self.infer(unit, value)
				# If inference is True, call backtrack
				if inference == True:
					#print("Assign ", value, " to ", unit)
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
					#print(unit, " reference return false at ", value)
					self.sigma = copy_sigma
					self.solution = copy_solution
			self.sigma[unit].remove(value)
			self.solution[unit] = 0
		#print(unit, " fail to assign")
		return False

	# This function check if assigning the value to the spot will cause conflict
	def consistent(self, spot, value, solution):
		peer_list = self.grid.peers[spot]
		for (peerx, peery) in peer_list:
			index = (peerx,peery)
			if solution[index]!=0 and value == solution[index]:
				#print(spot, " conflicts with ", index, " at ", value)
				return False
		return True

	# Based on the choice for the spot, eliminate the domain for its peers and check for future decisions' result based on this choice
	def infer(self, spot, value):
		peer_list = self.grid.peers[spot]
		for i in peer_list:
			if self.solution[i]!=0:
				continue
			else:
				if value in self.sigma[i]:
					#print(value, " is removed from ",i)
					# Remove the choice from peer's domain
					self.sigma[i].remove(value)
					# If the peer ends up only having one choice, check it
					if len(self.sigma[i])==1:
						# If the one left choice for the peer is consistent for the current assignment, check for future decisions' based on this choice
						if self.consistent(i, self.sigma[i][0], self.solution) == True:
							self.solution[i] = self.sigma[i][0]
							#print("Call infer on ", (i[0],i[1]), " by assiging it to ", self.sigma[(i[0],i[1])][0])
							result = self.infer(i, self.sigma[i][0])
							if result == False:
								return False
							#print("Assign ", self.sigma[i][0], " to ", i)
						# Not consistent, all previous choices lead to this failure, redo previous decisions
						else:
							#print(spot, " can not be asigned ", value, " due to the conflict that causes by ", (i[0],i[1]))
							return False
					# The peer ends up with no choice, bad decision
					elif len(self.sigma[i])==0:
						#print(spot, "causes ",(i[0],i[1]), "to have no option")
						return False
					else:
						continue
		return True

	# This function check if the assignment is complete
	def check_complete(self, solution):
		for i in range(1,10):
			for j in range(1,10):
				if solution[(i,j)] == 0:
					return False
		return True

	# This function return an unassigned spot, it will choose the one with the least amount of domain
	def get_unassigned_spot(self, sigma):
		domain_length = 10
		unassigned_spot = 0
		for (i,j) in sigma:
			if self.solution[(i,j)]==0:
				if len(sigma[(i,j)])<domain_length:
					unassigned_spot = (i,j)
					domain_length = len(sigma[(i,j)])
		return unassigned_spot

	# This function translate self.solution to the one that can be used for display()
	def tranverse_solution(self):
		return_solution = {}
		for i in range(1,10):
			for j in range(1,10):
				array = []
				array.append(self.solution[(i,j)])
				return_solution[(i,j)]=array
		return return_solution

easy = ["..3.2.6..9..3.5..1..18.64....81.29..7.......8..67.82....26.95..8..2.3..9..5.1.3..",
"2...8.3...6..7..84.3.5..2.9...1.54.8.........4.27.6...3.1..7.4.72..4..6...4.1...3",
"36..2..89...361............8.3...6.24..6.3..76.7...1.8............418...97..3..14",
".....3.17.15..9..8.6.......1....7.....9...2.....5....4.......2.5..6..34.34.2.....",
"...1254....84.....42.8......3.....95.6.9.2.1.51.....6......3.49.....72....1298..."]

hard = ['4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......',
 '52...6.........7.13...........4..8..6......5...........418.........3..2...87.....',
 '6.....8.3.4.7.................5.4.7.3..2.....1.6.......2.....5.....8.6......1....',
 '48.3............71.2.......7.5....6....2..8.............1.76...3.....4......5....',
 '....14....3....2...7..........9...3.6.1.............8.2.....1.4....5.6.....7.8...',
 '......52..8.4......3...9...5.1...6..2..7........3.....6...1..........7.4.......3.',
 '6.2.5.........3.4..........43...8....1....2........7..5..27...........81...6.....',
 '.524.........7.1..............8.2...3.....6...9.5.....1.6.3...........897........',
 '6.2.5.........4.3..........43...8....1....2........7..5..27...........81...6.....',
 '.923.........8.1...........1.7.4...........658.........6.5.2...4.....7.....9.....',
 '6..3.2....5.....1..........7.26............543.........8.15........4.2........7..',
 '.6.5.1.9.1...9..539....7....4.8...7.......5.8.817.5.3.....5.2............76..8...',
 '..5...987.4..5...1..7......2...48....9.1.....6..2.....3..6..2.......9.7.......5..',
 '3.6.7...........518.........1.4.5...7.....6.....2......2.....4.....8.3.....5.....',
 '1.....3.8.7.4..............2.3.1...........958.........5.6...7.....8.2...4.......',
 '6..3.2....4.....1..........7.26............543.........8.15........4.2........7..',
 '....3..9....2....1.5.9..............1.2.8.4.6.8.5...2..75......4.1..6..3.....4.6.',
 '45.....3....8.1....9...........5..9.2..7.....8.........1..4..........7.2...6..8..',
 '.237....68...6.59.9.....7......4.97.3.7.96..2.........5..47.........2....8.......',
 '..84...3....3.....9....157479...8........7..514.....2...9.6...2.5....4......9..56',
 '.98.1....2......6.............3.2.5..84.........6.........4.8.93..5...........1..',
 '..247..58..............1.4.....2...9528.9.4....9...1.........3.3....75..685..2...',
 '4.....8.5.3..........7......2.....6.....5.4......1.......6.3.7.5..2.....1.9......',
 '.2.3......63.....58.......15....9.3....7........1....8.879..26......6.7...6..7..4',
 '1.....7.9.4...72..8.........7..1..6.3.......5.6..4..2.........8..53...7.7.2....46',
 '4.....3.....8.2......7........1...8734.......6........5...6........1.4...82......',
 '.......71.2.8........4.3...7...6..5....2..3..9........6...7.....8....4......5....',
 '6..3.2....4.....8..........7.26............543.........8.15........8.2........7..',
 '.47.8...1............6..7..6....357......5....1..6....28..4.....9.1...4.....2.69.',
 '......8.17..2........5.6......7...5..1....3...8.......5......2..4..8....6...3....',
 '38.6.......9.......2..3.51......5....3..1..6....4......17.5..8.......9.......7.32',
 '...5...........5.697.....2...48.2...25.1...3..8..3.........4.7..13.5..9..2...31..',
 '.2.......3.5.62..9.68...3...5..........64.8.2..47..9....3.....1.....6...17.43....',
 '.8..4....3......1........2...5...4.69..1..8..2...........3.9....6....5.....2.....',
 '..8.9.1...6.5...2......6....3.1.7.5.........9..4...3...5....2...7...3.8.2..7....4',
 '4.....5.8.3..........7......2.....6.....5.8......1.......6.3.7.5..2.....1.8......',
 '1.....3.8.6.4..............2.3.1...........958.........5.6...7.....8.2...4.......',
 '1....6.8..64..........4...7....9.6...7.4..5..5...7.1...5....32.3....8...4........',
 '249.6...3.3....2..8.......5.....6......2......1..4.82..9.5..7....4.....1.7...3...',
 '...8....9.873...4.6..7.......85..97...........43..75.......3....3...145.4....2..1',
 '...5.1....9....8...6.......4.1..........7..9........3.8.....1.5...2..4.....36....',
 '......8.16..2........7.5......6...2..1....3...8.......2......7..3..8....5...4....',
 '.476...5.8.3.....2.....9......8.5..6...1.....6.24......78...51...6....4..9...4..7',
 '.....7.95.....1...86..2.....2..73..85......6...3..49..3.5...41724................',
 '.4.5.....8...9..3..76.2.....146..........9..7.....36....1..4.5..6......3..71..2..',
 '.834.........7..5...........4.1.8..........27...3.....2.6.5....5.....8........1..',
 '..9.....3.....9...7.....5.6..65..4.....3......28......3..75.6..6...........12.3.8',
 '.26.39......6....19.....7.......4..9.5....2....85.....3..2..9..4....762.........4',
 '2.3.8....8..7...........1...6.5.7...4......3....1............82.5....6...1.......',
 '6..3.2....1.....5..........7.26............843.........8.15........8.2........7..',
 '1.....9...64..1.7..7..4.......3.....3.89..5....7....2.....6.7.9.....4.1....129.3.',
 '.........9......84.623...5....6...453...1...6...9...7....1.....4.5..2....3.8....9',
 '.2....5938..5..46.94..6...8..2.3.....6..8.73.7..2.........4.38..7....6..........5',
 '9.4..5...25.6..1..31......8.7...9...4..26......147....7.......2...3..8.6.4.....9.',
 '...52.....9...3..4......7...1.....4..8..453..6...1...87.2........8....32.4..8..1.',
 '53..2.9...24.3..5...9..........1.827...7.........981.............64....91.2.5.43.',
 '1....786...7..8.1.8..2....9........24...1......9..5...6.8..........5.9.......93.4',
 '....5...11......7..6.....8......4.....9.1.3.....596.2..8..62..7..7......3.5.7.2..',
 '.47.2....8....1....3....9.2.....5...6..81..5.....4.....7....3.4...9...1.4..27.8..',
 '......94.....9...53....5.7..8.4..1..463...........7.8.8..7.....7......28.5.26....',
 '.2......6....41.....78....1......7....37.....6..412....1..74..5..8.5..7......39..',
 '1.....3.8.6.4..............2.3.1...........758.........7.5...6.....8.2...4.......',
 '2....1.9..1..3.7..9..8...2.......85..6.4.........7...3.2.3...6....5.....1.9...2.5',
 '..7..8.....6.2.3...3......9.1..5..6.....1.....7.9....2........4.83..4...26....51.',
 '...36....85.......9.4..8........68.........17..9..45...1.5...6.4....9..2.....3...',
 '34.6.......7.......2..8.57......5....7..1..2....4......36.2..1.......9.......7.82',
 '......4.18..2........6.7......8...6..4....3...1.......6......2..5..1....7...3....',
 '.4..5..67...1...4....2.....1..8..3........2...6...........4..5.3.....8..2........',
 '.......4...2..4..1.7..5..9...3..7....4..6....6..1..8...2....1..85.9...6.....8...3',
 '8..7....4.5....6............3.97...8....43..5....2.9....6......2...6...7.71..83.2',
 '.8...4.5....7..3............1..85...6.....2......4....3.26............417........',
 '....7..8...6...5...2...3.61.1...7..2..8..534.2..9.......2......58...6.3.4...1....',
 '......8.16..2........7.5......6...2..1....3...8.......2......7..4..8....5...3....',
 '.2..........6....3.74.8.........3..2.8..4..1.6..5.........1.78.5....9..........4.',
 '.52..68.......7.2.......6....48..9..2..41......1.....8..61..38.....9...63..6..1.9',
 '....1.78.5....9..........4..2..........6....3.74.8.........3..2.8..4..1.6..5.....',
 '1.......3.6.3..7...7...5..121.7...9...7........8.1..2....8.64....9.2..6....4.....',
 '4...7.1....19.46.5.....1......7....2..2.3....847..6....14...8.6.2....3..6...9....',
 '......8.17..2........5.6......7...5..1....3...8.......5......2..3..8....6...4....',
 '963......1....8......2.5....4.8......1....7......3..257......3...9.2.4.7......9..',
 '15.3......7..4.2....4.72.....8.........9..1.8.1..8.79......38...........6....7423',
 '..........5724...98....947...9..3...5..9..12...3.1.9...6....25....56.....7......6',
 '....75....1..2.....4...3...5.....3.2...8...1.......6.....1..48.2........7........',
 '6.....7.3.4.8.................5.4.8.7..2.....1.3.......2.....5.....7.9......1....',
 '....6...4..6.3....1..4..5.77.....8.5...8.....6.8....9...2.9....4....32....97..1..',
 '.32.....58..3.....9.428...1...4...39...6...5.....1.....2...67.8.....4....95....6.',
 '...5.3.......6.7..5.8....1636..2.......4.1.......3...567....2.8..4.7.......2..5..',
 '.5.3.7.4.1.........3.......5.8.3.61....8..5.9.6..1........4...6...6927....2...9..',
 '..5..8..18......9.......78....4.....64....9......53..2.6.........138..5....9.714.',
 '..........72.6.1....51...82.8...13..4.........37.9..1.....238..5.4..9.........79.',
 '...658.....4......12............96.7...3..5....2.8...3..19..8..3.6.....4....473..',
 '.2.3.......6..8.9.83.5........2...8.7.9..5........6..4.......1...1...4.22..7..8.9',
 '.5..9....1.....6.....3.8.....8.4...9514.......3....2..........4.8...6..77..15..6.',
 '.....2.......7...17..3...9.8..7......2.89.6...13..6....9..5.824.....891..........',
 '3...8.......7....51..............36...2..4....7...........6.13..452...........8..']

#The display below has a mess of comments. I implement a for loop to run all the hard problem
#and count run time for each solution. A few problem might cause over 10s to solve, but the solver
# should be able to solve most of the problem under 10s

#feedback = []
print("====Problem====")
#for problem in hard:
	#g = Grid(problem)
	#g.display()
	#s = Solver(g)
g = Grid(hard[1])
#Display the original problem
g.display()
s = Solver(g)
#print(s.grid.domains[(3,3)])
#print(s.sigma)
	#start = time.time()
if s.solve():
	print("====Solution===")
	#Display the solution
	#Feel free to call other functions to display
	g.domains = s.tranverse_solution()
	g.display()
	#process = subprocess.Popen(["./picosat-965/picosat", "./cnf/hard1.cnf"],stdout=subprocess.PIPE)
else:
	print("==No solution==")
	#g.domains = s.tranverse_solution()
	#g.display()
	#end = time.time()
	#print("Solver solves for ", end-start)
	#if end-start > 10:
		#feedback.append(hard.index(problem))
		#print("Problem ", hard.index(problem), " exceed 10s")
#if len(feedback)==0:
	#print("Every Problem solved under 10s")
#else:
	#for i in feedback:
		#print("Problem", i, " exceed 10s")
	

