# map.py

import random
from maze_generator import generate_maze, widen_maze
from settings import CORRIDOR_WIDTH

class Map:
    def __init__(self, width, height):
        self.corridor_width = CORRIDOR_WIDTH
        coarse_maze = generate_maze(width, height)
        if self.corridor_width > 1:
            self.grid = widen_maze(coarse_maze, corridor_width=self.corridor_width)
        else:
            self.grid = coarse_maze
        self.width = len(self.grid[0])
        self.height = len(self.grid)

    def is_wall(self, x, y):
        ix, iy = int(x), int(y)
        if ix < 0 or iy < 0 or ix >= self.width or iy >= self.height:
            return True
        return self.grid[iy][ix] == '#'

    def get_grid(self):
        return self.grid

    def get_start_pos(self):
        # Find first open cell
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == ' ':
                    return (x + 0.5, y + 0.5)

    def find_random_empty(self, avoid=None):
        empty = []
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == ' ':
                    if avoid is not None and (x, y) in avoid:
                        continue
                    empty.append((x, y))
        if not empty:
            raise Exception('No empty cell in map')
        x, y = random.choice(empty)
        return (x + 0.5, y + 0.5)