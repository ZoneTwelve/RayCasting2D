# maze_generator.py

import random
from settings import CORRIDOR_WIDTH

def generate_maze(width, height):
    """
    Generates a maze using DFS backtracking.
    '#' = wall, ' ' = open path.
    Assumes width/height are odd numbers >= 3.
    """
    maze = [['#' for _ in range(width)] for _ in range(height)]

    def neighbors(cx, cy):
        n = []
        for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            nx, ny = cx + dx, cy + dy
            if 1 <= nx < width-1 and 1 <= ny < height-1 and maze[ny][nx] == '#':
                n.append((nx, ny, dx, dy))
        return n

    stack = []
    sx, sy = 1, 1
    maze[sy][sx] = ' '
    stack.append((sx, sy))

    while stack:
        x, y = stack[-1]
        neigh = neighbors(x, y)
        if neigh:
            nx, ny, dx, dy = random.choice(neigh)
            maze[y + dy//2][x + dx//2] = ' '
            maze[ny][nx] = ' '
            stack.append((nx, ny))
        else:
            stack.pop()

    return maze

def widen_maze(cells, corridor_width=2):
    """Expands each path cell into a (corridor_width x corridor_width) block."""
    in_h = len(cells)
    in_w = len(cells[0])
    out_h = in_h * corridor_width
    out_w = in_w * corridor_width
    out = [['#' for _ in range(out_w)] for _ in range(out_h)]
    for y in range(in_h):
        for x in range(in_w):
            if cells[y][x] == ' ':
                for dy in range(corridor_width):
                    for dx in range(corridor_width):
                        out[y*corridor_width+dy][x*corridor_width+dx] = ' '
    return out