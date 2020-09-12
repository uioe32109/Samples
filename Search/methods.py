    from __future__ import print_function
#Use priority queues from Python libraries, don't waste time implementing your own
import heapq
from heapq import *
import math
from collections import deque
ACTIONS = [(0,-1),(-1,0),(0,1),(1,0)]

class Agent:
    def __init__(self, grid, start, goal, type):
        self.grid = grid
        self.previous = {}
        self.explored = []
        self.start = start 
        self.grid.nodes[start].start = True
        self.goal = goal
        self.grid.nodes[goal].goal = True
        self.new_plan(type)
    def new_plan(self, type):
        self.finished = False
        self.failed = False
        self.type = type
        if self.type == "dfs" :
            self.frontier = [self.start]
            self.explored = []
        elif self.type == "bfs":
            self.frontier = deque([self.start])
            self.explored = []
        elif self.type == "ucs":
            self.frontier = []
            heappush(self.frontier,(0,self.start))
            self.explored = []
        elif self.type == "astar":
            H = self.getH(self.start[0], self.start[1], self.goal[0], self.goal[1])
            self.frontier = []
            heappush(self.frontier, (H, self.start))
            self.explored = []
    def show_result(self):
        current = self.goal
        while not current == self.start:
            current = self.previous[current]
            self.grid.nodes[current].in_path = True #This turns the color of the node to red
    def make_step(self):
        if self.type == "dfs":
            self.dfs_step()
        elif self.type == "bfs":
            self.bfs_step()
        elif self.type == "ucs":
            self.ucs_step()
        elif self.type == "astar":
            self.astar_step()
    def dfs_step(self):
        #If frontier is empty before goal is found, no path
        if not self.frontier:
            self.failed = True
            print("no path")
            return
        current = self.frontier.pop()
        print("current node: ", current)
        #Update the explored node's status
        self.grid.nodes[current].checked = True
        self.grid.nodes[current].frontier = False
        self.explored.append(current)
        children = [(current[0]+a[0], current[1]+a[1]) for a in ACTIONS]
        #Explore the children
        for node in children:
            #If the node is explored before, ignore it
            if node in self.explored or node in self.frontier:
                print("explored before: ", node)
                continue
            #If the node is in proper range
            if node[0] in range(self.grid.row_range) and node[1] in range(self.grid.col_range):
                #Find a puddle, node not accessible
                if self.grid.nodes[node].puddle:
                    print("puddle at: ", node)
                else:
                    #Record the parent node for the child
                    self.previous[node] = current
                    #Check if this node is the goal
                    if node == self.goal:
                        self.finished = True
                        return
                    else:
                        #Add new node into frontier
                        self.frontier.append(node)
                        #Update the status that the node is in frontier
                        self.grid.nodes[node].frontier = True
            else:
                print("out of range: ", node)
    def bfs_step(self):
        #If the frontier is empty before goal is found, no path
        if not self.frontier:
            self.failed = True
            print("no path")
            return
        current = self.frontier.popleft()
        #Update popped node's status
        self.grid.nodes[current].checked = True
        self.grid.nodes[current].frontier = False
        #Add the popped node into explored
        self.explored.append(current)
        children = [(current[0]+a[0], current[1]+a[1]) for a in ACTIONS]
        #Explore the children 
        for node in children:
            #If the node is explored, ignore it
            if node in self.explored or node in self.frontier:
                print("explored before: ", node)
                continue
            #If the node is in proper range
            if node[0] in range(self.grid.row_range) and node[1] in range(self.grid.col_range):
                #Find a puddle, node is not accessible
                if self.grid.nodes[node].puddle:
                    print("puddle at: ", node)
                else:
                    #Record parent node for the child
                    self.previous[node] = current
                    #Check if the child is the goal
                    if node == self.goal:
                        self.finished = True
                        return
                    else:
                        #Add child into frontier
                        self.frontier.append(node)
                        #Update the status that the node is in frontier
                        self.grid.nodes[node].frontier = True
            else:
                print("out of range: ", node)


    def ucs_step(self):
        #[Hint] you can get the cost of a node by node.cost()
        #If frontier is empty before goal is found, no path is available
        if not self.frontier:
            self.failed = True
            print("no path")
            return
        #Pop the least cost node from frontier
        comb = heappop(self.frontier)
        path_cost = comb[0]
        current = comb[1]
        self.grid.nodes[current].checked = True
        self.grid.nodes[current].frontier = False

        #Add popped node into explored
        self.explored.append(current)
        #Get children's coordinates
        children = [(current[0]+a[0], current[1]+a[1]) for a in ACTIONS]
        #Explore the children
        for node in children:
            if node[0] in range(self.grid.row_range) and node[1] in range(self.grid.col_range):
                #The cost from starting point to this child
                temp_cost = path_cost + self.grid.nodes[node].cost()
                #Check if the child is the goal
                if node == self.goal:
                    self.finished = True
                    self.previous[node]=current
                    print("Path cost: ", path_cost+self.grid.nodes[node].cost())
                    return
                #If the child is a puddle, ignore
                elif self.grid.nodes[node].puddle:
                    continue
                #If the child is explored, ignore
                elif node in self.explored:
                    continue
                else:
                    #Check if an unexplored child has already been added into frontier
                    is_in_frontier = 0
                    for i in range(len(self.frontier)):
                        if self.frontier[i][1] == node:
                            is_in_frontier = 1
                            #The child is in frontier and has higher cost, replace it with current child
                            if temp_cost < self.frontier[i][0]:
                                self.frontier[i] = (temp_cost, node)
                                self.previous[node] = current
                    #If the child is not explored or in frontier, add it into frontier
                    if is_in_frontier == 0:
                        self.previous[node]=current
                        heappush(self.frontier, (temp_cost, node))
                        self.grid.nodes[node].frontier = True           

           
    def astar_step(self):
        #[Hint] you need to declare a heuristic function for Astar
        #If frontier is empty before goal is found, no path is available
        if not self.frontier:
            self.failed = True
            print("no path")
            return
        #Pop the least cost node from frontier
        comb = heappop(self.frontier)
        path_cost = comb[0]
        current = comb[1]
        self.grid.nodes[current].checked = True
        self.grid.nodes[current].frontier = False
        #H value for the current node
        H_current = self.getH(current[0], current[1], self.goal[0],self.goal[1])
        #Current node's real cost
        current_real_cost = path_cost - H_current
        #Add popped node into explored
        self.explored.append(current)
        #Get children's coordinates
        children = [(current[0]+a[0], current[1]+a[1]) for a in ACTIONS]
        #Explore the children
        for node in children:
            if node[0] in range(self.grid.row_range) and node[1] in range(self.grid.col_range):
                #H value for the child
                H = self.getH(node[0], node[1], self.goal[0], self.goal[1])
                #Real cost of the child
                child_cost = self.grid.nodes[node].cost()
                #Heuristic cost for reaching the child
                temp_cost = current_real_cost + child_cost + H
                #Check if the child is the goal
                if node == self.goal:
                    self.finished = True
                    self.previous[node]=current
                    print("Path cost: ", current_real_cost + child_cost)
                    return
                #If the child is a puddle, ignore
                elif self.grid.nodes[node].puddle:
                    continue
                #If the child is explored, ignore
                elif node in self.explored:
                    continue
                else:
                    #Check if an unexplored child has already been added into frontier
                    is_in_frontier = 0
                    for i in range(len(self.frontier)):
                        if self.frontier[i][1] == node:
                            is_in_frontier = 1
                            #The child is in frontier and has higher cost, replace it with current child
                            if temp_cost < self.frontier[i][0]:
                                self.frontier[i] = (temp_cost, node)
                                self.previous[node] = current
                    #If the child is not explored or in frontier, add it into frontier
                    if is_in_frontier == 0:
                        self.previous[node]=current
                        heappush(self.frontier, (temp_cost, node))
                        self.grid.nodes[node].frontier = True
                   
    def getH(self, x_start, y_start, x_finish, y_finish):
        #d1 = x_finish - x_start
        #d2 = y_finish - y_start
        #square1 = d1 ** 2
        #square2 = d2 ** 2
        #squareroot = math.sqrt(square1 + square2)
        #return squareroot
        d1 = abs(x_finish - x_start)
        d2 = abs(y_finish - y_start)
        return (d1 + d2) * 10

