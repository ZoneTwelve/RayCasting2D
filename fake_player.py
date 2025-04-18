# fake_player.py

import math
import random
from sprite_object import SpriteObject
from settings import FAKE_PLAYER_SPEED, FAKE_PLAYER_RADIUS
from utils import clamp

class FakePlayer(SpriteObject):
    def __init__(self, x, y, map_obj, color, radius=FAKE_PLAYER_RADIUS):
        super().__init__(x, y, color, radius)
        self.map = map_obj
        self.angle = random.uniform(0, 2 * math.pi)
        self.move_speed = FAKE_PLAYER_SPEED
        self.wander_time = 0.0
        self._pick_new_direction()

    def _pick_new_direction(self):
        self.target_dir = random.uniform(0, 2 * math.pi)
        self.wander_time = random.uniform(0.4, 1.3)

    def update(self, dt):
        # Periodically pick a new random direction
        self.wander_time -= dt
        if self.wander_time <= 0:
            self._pick_new_direction()

        # Move forward, with collision avoidance
        dx = math.cos(self.target_dir) * self.move_speed * dt
        dy = math.sin(self.target_dir) * self.move_speed * dt

        if not self._has_collision(self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy
        else:
            # Hit; try to bounce off in new dir next update
            self._pick_new_direction()

    def _has_collision(self, x, y):
        # Check four corners for collisions (circle vs grid)
        r = self.radius
        for ox in (-r, r):
            for oy in (-r, r):
                tx = x + ox
                ty = y + oy
                if self.map.is_wall(tx, ty):
                    return True
        return False