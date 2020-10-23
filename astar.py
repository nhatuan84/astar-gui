import cv2
import numpy as np
import random as r


IMG_H = 400
IMG_W = 800


GRID_SIZE = 10
GRID_H = int(IMG_H/GRID_SIZE)
GRID_W = int(IMG_W/GRID_SIZE)
print(GRID_H, GRID_W)


def makeGrid():
    grid = np.zeros((GRID_H,GRID_W)).astype(np.uint8).tolist()
    return grid


def genObs(grid, obs=10):
    for i in range(obs):
        # -1 for index
        y = r.randint(2, GRID_H-1)-1
        x = r.randint(2, GRID_W-1)-1
        grid[y][x] = 1
    return grid

def drawGrid2(image, grid):
    #print(len(grid))
    #print(len(grid[0]))
    #H
    for i in range(len(grid)):
        #W
        for j in range(len(grid[i])):
            start_point = (j*GRID_SIZE, i*GRID_SIZE)
            end_point = ((j+1)*GRID_SIZE, (i+1)*GRID_SIZE)
            if(grid[i][j] == 1):
                image = cv2.rectangle(image, start_point, end_point, (0, 0, 255), -1)
            else:
                image = cv2.rectangle(image, start_point, end_point, (0, 255, 0), 1)
    return image


def drawAt(image, x, y, color=(255, 0, 0)):
    within_range_criteria = [
        x > GRID_W,
        x < 0,
        y > GRID_H,
        y < 0,
    ]
    
    if any(within_range_criteria):
        print('error within_range_criteria')
        return image  

    start_point = (GRID_SIZE*(x-1), GRID_SIZE*(y-1)) 
    end_point = (GRID_SIZE*x, GRID_SIZE*y) 
    image = cv2.rectangle(image, start_point, end_point, color, -1)
    return image 

def drawStartEnd(image, start, end):
    image = drawAt(image, start[0], start[1], color=(255, 0, 255))
    image = drawAt(image, end[0], end[1], color=(0, 128, 255))
    return image


def done(image):
    font = cv2.FONT_HERSHEY_SIMPLEX 
    org = (IMG_W//2, IMG_H//2) 
    image = cv2.putText(image, 'Done', org, font, 0.5, (255, 0, 255) , 2, cv2.LINE_AA) 
    return image

class Node:

    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position
        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position

def return_path(image,current_node):
    path = []
    current = current_node
    while current is not None:
        image = drawAt(image, current.position[0]+1, current.position[1]+1,color=(0, 0, 0))
        cv2.imshow('', image)
        cv2.waitKey(0)
        path.append(current.position)
        current = current.parent
    return path[::-1]  # Return reversed path


def astar(image, grid, start, end):
    new_start = (start[0]-1, start[1]-1)
    new_end = (end[0]-1, end[1]-1)
    # Create start and end node
    start_node = Node(None, new_start)
    start_node.g = start_node.h = start_node.f = 0
    end_node = Node(None, new_end)
    end_node.g = end_node.h = end_node.f = 0

    # Initialize both open and closed list
    open_list = []
    closed_list = []

    # Add the start node
    open_list.append(start_node)

    # Adding a stop condition
    outer_iterations = 0
    max_iterations = (min(GRID_H, GRID_W) // 2) ** 2

    adjacent_squares = ((0, -1), (0, 1), (-1, 0), (1, 0),)
    #adjacent_squares = ((0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1),)

    # Loop until you find the end
    while len(open_list) > 0:
        outer_iterations += 1
        
        # Get the current node
        current_node = open_list[0]
        current_index = 0
        for index, item in enumerate(open_list):
            if item.f < current_node.f:
                current_node = item
                current_index = index

        if outer_iterations > max_iterations:
            print("giving up on pathfinding too many iterations")
            return return_path(image, current_node)

        # Pop current off open list, add to closed list
        open_list.pop(current_index)
        closed_list.append(current_node)

        # Found the goal
        if current_node == end_node:
            image = done(image)
            cv2.imshow('', image)
            cv2.waitKey(0) 
            return return_path(image, current_node)

        image = drawAt(image, current_node.position[0]+1, current_node.position[1]+1)
        cv2.imshow('', image)
        cv2.waitKey(0)   

        # Generate children
        children = []

        for new_position in adjacent_squares:  # Adjacent squares

            # Get node position
            node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])

            # Make sure within range
            within_range_criteria = [
                current_node.position[0] > GRID_W,
                current_node.position[0] < 0,
                current_node.position[1] > GRID_H,
                current_node.position[1] < 0,
            ]
            
            if any(within_range_criteria):
                continue

            # Make sure walkable terrain
            
            if grid[node_position[1]][node_position[0]] != 0:
                continue

            # Create new node
            new_node = Node(current_node, node_position)

            # Append
            children.append(new_node)

        # Loop through children
        for child in children:
            
            # Child is on the closed list
            if len([closed_child for closed_child in closed_list if closed_child == child]) > 0:
                continue

            # Create the f, g, and h values
            child.g = current_node.g + 1
            child.h = ((child.position[0] - end_node.position[0]) ** 2) + \
                      ((child.position[1] - end_node.position[1]) ** 2)
            child.f = child.g + child.h

            # Child is already in the open list
            if len([open_node for open_node in open_list if child == open_node and child.g > open_node.g]) > 0:
                continue

            # Add the child to the open list
            open_list.append(child)


        
def main():
    grid = makeGrid()
    grid = genObs(grid, obs=200)
    image = np.ones((IMG_H, IMG_W, 3))
    image = drawGrid2(image, grid)
    start = (1, 1)
    end = (50, 35)
    image = drawStartEnd(image, start, end)
    astar(image, grid, start, end)

    cv2.imshow('', image)
    cv2.waitKey(0)

main()
