import pygame, sys, random

class Node: # Basically squares comprising the maze
    def __init__(self, row, col, size):
        self.m_row = row
        self.m_col = col
        self.m_size = size
        self.visited = False
        # Adding walls
        self.m_walls = {} # keys are cardinal directions and value is adjacent Node
        self.x = self.m_size*self.m_col+self.m_size
        self.y = self.m_size*self.m_row+self.m_size

    def connections(self):
        m_list = []
        for k,v in self.m_walls.items():
            if v:
                m_list.append([k, v])
        return m_list

    def draw(self, screen):
        if self.m_walls["north"]:
            start_pos = (self.x, self.y)
            end_pos = (self.x+self.m_size, self.y)
            pygame.draw.line(screen, (0,0,0), start_pos, end_pos, 1)
        if self.m_walls["south"]:
            start_pos = (self.x, self.y+self.m_size)
            end_pos = (self.x+self.m_size, self.y+self.m_size)
            pygame.draw.line(screen, (0,0,0), start_pos, end_pos, 1)
        if self.m_walls["east"]:
            start_pos = (self.x+self.m_size, self.y)
            end_pos = (self.x+self.m_size, self.y+self.m_size)
            pygame.draw.line(screen, (0,0,0), start_pos, end_pos, 1)
        if self.m_walls["west"]:
            start_pos = (self.x, self.y)
            end_pos = (self.x, self.y+self.m_size)
            pygame.draw.line(screen, (0,0,0), start_pos, end_pos, 1)

    def updateWalls(self, key):
        self.m_walls[key] = None

    def getVisited(self):
        return self.visited

    def updateVisited(self):
        self.visited = True

class Maze: # 2-d array of squares
    def __init__(self, num_rows, num_cols, node_size):
        self.m_num_rows = num_rows
        self.m_num_cols = num_cols
        self.m_node_size = node_size
        self.rand_x = random.randrange(num_cols)
        self.m_nodes = [ [Node(i, j, self.m_node_size) for j in range(self.m_num_cols)] \
                                                       for i in range(self.m_num_rows)]

    def connect_nodes_default(self): # By connecting, we mean creating walls in each node's hash
        for node in self.iter_node(): # iter_node is a generator
            node.m_walls["north"] = self.get_node(node.m_row-1, node.m_col) # If nothing north then none
            node.m_walls["south"] = self.get_node(node.m_row+1, node.m_col)
            node.m_walls["east"] = self.get_node(node.m_row, node.m_col+1)
            node.m_walls["west"] = self.get_node(node.m_row, node.m_col-1)

    def get_node(self, row, col):
        if row>=0 and col>=0 and row<self.m_num_rows and col<self.m_num_cols:
            return self.m_nodes[row][col]
        return None

    def iter_node(self): # Done because it's going to be done alot. Nested for loop is inefficient
        for i in range(self.m_num_rows):
            for j in range(self.m_num_cols):
                yield self.m_nodes[i][j]

    def draw(self, screen):
        self.draw_outer_boundary(screen)
        self.draw_openings(screen)
        for node in self.iter_node():
            node.draw(screen)

    def draw_outer_boundary(self, screen): # Drawing a thick line around the maze
        topLeft = (self.m_node_size, self.m_node_size)
        topRight = (self.m_node_size + self.m_node_size*self.m_num_cols, self.m_node_size)
        botLeft = (self.m_node_size, self.m_node_size + self.m_node_size*self.m_num_rows)
        botRight =(self.m_node_size + self.m_node_size*self.m_num_cols, \
                      self.m_node_size + self.m_node_size*self.m_num_rows)
        pygame.draw.line(screen, (0,0,0), topLeft, topRight, 5) # Surface, color, start point, end point, pxl size
        pygame.draw.line(screen, (0,0,0), topLeft, botLeft, 5)
        pygame.draw.line(screen, (0,0,0), topRight, botRight, 5)
        pygame.draw.line(screen, (0,0,0), botLeft, botRight, 5)

    def draw_openings(self, screen):
        rand1 = self.m_node_size + self.rand_x*self.m_node_size
        rand2 = self.m_node_size + (self.m_num_cols//2)*self.m_node_size + random.randrange(0, 3)*self.m_node_size
        topLine = ((rand1, self.m_node_size), (rand1 + self.m_node_size, self.m_node_size))
        botLine = ((rand2, self.m_node_size + self.m_node_size*self.m_num_rows),
                   (rand2 + self.m_node_size, self.m_node_size + self.m_node_size*self.m_num_rows))
        pygame.draw.line(screen, (255, 255, 255), topLine[0], topLine[1], 5)
        pygame.draw.line(screen, (255, 255, 255), botLine[0], botLine[1], 5)

    def generate_maze(self):
        # This is the function that uses DFS
        opp = {"north": "south", "south": "north",
               "east": "west", "west": "east"}
        queue = []
        current_node = self.m_nodes[0][self.rand_x]
        current_node.updateVisited()
        queue.append(current_node)
        path_length = 0
        while len(queue) != 0:
            adj_nodes = current_node.connections()
            random.shuffle(adj_nodes)
            for k,v in adj_nodes:
                if not v.getVisited():
                    path_length+=1
                    current_node.updateWalls(k)
                    v.updateWalls(opp[k])
                    current_node = v
                    current_node.updateVisited()
                    queue.append(current_node)
                    break
            else: # if all nearby nodes visited
                # Remove last index and go back through the queue
                queue.pop(-1)

                # Right here, attempting to add loops to maze
                # Changes it drastically, but dfs not good for mazes
                if adj_nodes and path_length >=8:
                    k, v = random.choice(adj_nodes)
                    current_node.updateWalls(k)
                    v.updateWalls(opp[k])
                path_length=0

                random_index = int(random.random()*len(queue))
                if len(queue) != 0:
                    queue[random_index], queue[-1] = queue[-1], queue[random_index]
                    current_node = queue[-1]


    def printme(self):
        for node in self.iter_node():
            print(node.m_row, node.m_col, node.connections())

def main():
    pygame.init()
    screen = pygame.display.set_mode((900, 600)) # Size of the screen
    screen.fill((255, 255, 255)) # Filling with white, must provide a typle

    num_rows = 35
    num_cols = 35
    node_size = 15 # Size of each of the squares; measured in pixels
    maze = Maze(num_rows, num_cols, node_size)
    maze.connect_nodes_default() # Each node needs to be connected to its adjacent node
    #maze.printme()

    # DFS Implementation
    maze.generate_maze()

    maze.draw(screen)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        pygame.display.update()
    pygame.quit()
    sys.exit()


main()
