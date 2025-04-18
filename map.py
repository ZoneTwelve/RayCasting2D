# map.py

import random
from maze_generator import generate_maze

class Map:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = generate_maze(width, height)

    def is_wall(self, x, y):
        """Return True if (x, y) is wall or out of bounds."""
        ix, iy = int(x), int(y)
        if ix < 0 or iy < 0 or ix >= self.width or iy >= self.height:
            return True
        return self.grid[iy][ix] == '#'
    
    def get_grid(self):
        return self.grid

    def get_start_pos(self):
        """Return a starting open cell near (1,1)."""
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == ' ':
                    return (x + 0.5, y + 0.5)

    def find_random_empty(self, avoid=None):
        """Return a random open cell not in 'avoid' list of (x, y) grid coords."""
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