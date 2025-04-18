# maze_generator.py

import random

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