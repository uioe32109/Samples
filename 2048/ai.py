from __future__ import absolute_import, division, print_function
import copy
import random
MOVES = {0: 'up', 1: 'left', 2: 'down', 3: 'right'}
ACTIONS = [(0, -1), (-1, 0), (0, 1), (1, 0)]


class Gametree:
	"""main class for the AI"""
	# Hint: Two operations are important. Grow a game tree, and then compute minimax score.
	# Hint: To grow a tree, you need to simulate the game one step.
	# Hint: Think about the difference between your move and the computer's move.
	def __init__(self, root_state, depth_of_tree, current_score): 
		self.root = Simulator(root_state, current_score, 0, 0)
		self.depth_of_tree = depth_of_tree
		self.current_score = current_score

	# Method to grow the game tree
	def growTree(self, parent, depth, max_or_chance):
		if(parent.checkIfCanGo()==False):
			return
		# Only contruct to depth 3
		if(depth==3):
			return
		# Current parent node is max player
		if max_or_chance == 0:
			# Add 4 board state into children based on 4 direction operations
			for i in range(0,4):
				parent_node = copy.deepcopy(parent)
				child = Simulator(parent_node.tileMatrix, parent_node.total_points,1,i)
				child.move(i)
				# Only add the state when the operation actually change the board state
				if child.tileMatrix != parent.tileMatrix:
					parent.children.append(child)
					self.growTree(child, depth+1, 1)

		# Current parent node is chance player
		else:
			# Search through each index on the matrix
			for i in range(0,parent.board_size):
				for j in range(0,parent.board_size):
					# Add a child when it finds a 0 tile
					if parent.tileMatrix[i][j]==0:
						parent_node = copy.deepcopy(parent)
						child = Simulator(parent_node.tileMatrix, parent_node.total_points,0,0)
						child.tileMatrix[i][j]=2
						parent.children.append(child)
						self.growTree(child, depth+1, 0)


	# expectimax for computing best move
	# The value function should be able to pass extra point
	def minimax(self, node):
		# Deal with leaf node
		if len(node.children) == 0:
			# The board that is not in GameOver will go through the value function
			if node.checkIfCanGo() == True:
				return self.checkState(node.tileMatrix)
			else:
				return 0
		# Deal with max player node
		if node.max_or_chance == 0:
			value = -1
			result = -1
			choice = 0;
			for i in range(0, len(node.children)):
				result = self.minimax(node.children[i])
				# Pick the chance player that returns the highest value
				if value < result:
					value = result
					choice = i
			# Save the highest chance player for further implementations after function
			node.children[choice].evaluate = 1
			return value
		# Deal with chance player node
		else:
			value = 0
			# Add up all the value from max player and the possibility value 
			for i in node.children:
				value = value + self.minimax(i)*(1/len(node.children))
			return value
		
	# function to return best decision to game
	def compute_decision(self):
		# Grow the GameTree
		self.growTree(self.root, 0, 0)
		# Call minimax
		self.minimax(self.root)
		# Find the best chance player and return  which direction it performs
		for i in range(0, len(self.root.children)):
			if self.root.children[i].evaluate == 1:
				return self.root.children[i].direction

	# A evaluate function for a board state
	def checkState(self, tileMatrix):
		result = 0
		# Identical weight matrix to indicate the weight value for each index
		weight = [[6,5,4,3],[5,4,3,2],[4,3,2,1],[3,2,1,0]]
		# Add up the value base on the weight matrix
		# Idealy, the board that has the highest value on the left top corner has priority
		for i in range(0,4):
			for j in  range(0,4):
				result += tileMatrix[i][j] * weight[i][j]
		# If the value of difference between tiles is big, there's more penalty for the board state
		for x in range(0,4):
			for y in range(0,4):
				value = tileMatrix[x][y]
				if x-1>=0:
					result -= abs(value - tileMatrix[x-1][y])
				if x+1<=3:
					result -= abs(value - tileMatrix[x+1][y])
				if y-1>=0:
					result -= abs(value - tileMatrix[x][y-1])
				if y+1<=3:
					result -= abs(value - tileMatrix[x][y+1])
		return result


class Simulator:
	def __init__(self, currentMaxtrix, current_score, max_or_chance, direction):
		self.total_points = current_score;
		self.default_tile = 2
		self.board_size = 4
		self.tileMatrix = currentMaxtrix;
		self.children = []
		# This is a variable just for checking which chance player are picked to be the choice
		self.evaluate = 0
		# This is a variable to record the direction operation performed on a chance player
		self.direction = direction;
		# 0 is max player, 1 is chance player
		self.max_or_chance = max_or_chance;

	# Simulate Move
	def move(self, direction):
		for i in range(0, direction):
			self.rotateMatrixClockwise()
		if self.canMove():
			self.moveTiles()
			self.mergeTiles()
			#self.placeRandomTile()
		for j in range(0, (4 - direction) % 4):
			self.rotateMatrixClockwise()
	#Simulate rotateMatrixClockWise
	def rotateMatrixClockwise(self):
		tm = self.tileMatrix
		for i in range(0, int(self.board_size/2)):
			for k in range(i, self.board_size- i - 1):
				temp1 = tm[i][k]
				temp2 = tm[self.board_size - 1 - k][i]
				temp3 = tm[self.board_size - 1 - i][self.board_size - 1 - k]
				temp4 = tm[k][self.board_size - 1 - i]
				tm[self.board_size - 1 - k][i] = temp1
				tm[self.board_size - 1 - i][self.board_size - 1 - k] = temp2
				tm[k][self.board_size - 1 - i] = temp3
				tm[i][k] = temp4
	#Simulate moveTiles
	def moveTiles(self):
		tm = self.tileMatrix
		for i in range(0, self.board_size):
			for j in range(0, self.board_size - 1):
				while tm[i][j] == 0 and sum(tm[i][j:]) > 0:
					for k in range(j, self.board_size - 1):
						tm[i][k] = tm[i][k + 1]
					tm[i][self.board_size - 1] = 0
	#mergeTiles
	def mergeTiles(self):
		tm = self.tileMatrix
		for i in range(0, self.board_size):
			for k in range(0, self.board_size - 1):
				if tm[i][k] == tm[i][k + 1] and tm[i][k] != 0:
					tm[i][k] = tm[i][k] * 2
					tm[i][k + 1] = 0
					self.total_points += tm[i][k]
					self.moveTiles()
	#Simulate canMove
	def canMove(self):
		tm = self.tileMatrix
		for i in range(0, self.board_size):
			for j in range(1, self.board_size):
				if tm[i][j-1] == 0 and tm[i][j] > 0:
					return True
				elif (tm[i][j-1] == tm[i][j]) and tm[i][j-1] != 0:
					return True
		return False
	#Simulate placeRandomTile
	def placeRandomTile(self):
		while True:
			i = random.randint(0,self.board_size-1)
			j = random.randint(0,self.board_size-1)
			if self.tileMatrix[i][j] == 0:
				break
		self.tileMatrix[i][j] = 2
	#Simulate checkIfCanGo
	def checkIfCanGo(self):
		tm = self.tileMatrix
		for i in range(0, self.board_size ** 2):
			if tm[int(i / self.board_size)][i % self.board_size] == 0:
				return True
		for i in range(0, self.board_size):
			for j in range(0, self.board_size - 1):
				if tm[i][j] == tm[i][j + 1]:
					return True
				elif tm[j][i] == tm[j + 1][i]:
					return True
		return False
