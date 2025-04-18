# player.py

import math
from utils import clamp

class Player:
    def __init__(self, x, y, angle, radius, move_speed, rot_speed):
        self.x = x
        self.y = y
        self.angle = angle  # radians
        self.move_speed = move_speed
        self.rot_speed = rot_speed
        self.radius = radius  # used for collision

    def move(self, forward, strafe, game_map, dt):
        # forward, strafe = -1/0/1
        angle = self.angle
        dx = (math.cos(angle) * forward - math.sin(angle) * strafe) * self.move_speed * dt
        dy = (math.sin(angle) * forward + math.cos(angle) * strafe) * self.move_speed * dt
        self.try_move(dx, dy, game_map)

    def try_move(self, dx, dy, game_map):
        next_x = self.x + dx
        next_y = self.y + dy

        # Check collision X
        if not self._has_collision(next_x, self.y, game_map):
            self.x = next_x
        # Check collision Y
        if not self._has_collision(self.x, next_y, game_map):
            self.y = next_y

    def _has_collision(self, x, y, game_map):
        # Check for collision (circle vs grid)
        for ox in (-self.radius, self.radius):
            for oy in (-self.radius, self.radius):
                tx = x + ox
                ty = y + oy
                if game_map.is_wall(tx, ty):
                    return True
        return False

    def rotate(self, direction, dt):
        # direction: -1 = left, 1 = right
        self.angle += self.rot_speed * direction * dt
        self.angle %= (2 * math.pi)