import numpy as np
import random
import math
from player import Player
from settings import *
from map import Map
from raycaster import raycast_2d
from sprite_object import SpriteObject
from fake_player import FakePlayer

class HiderHunterEnv:
    def __init__(self, map_width=15, map_height=15, num_rays=15, max_steps=300):
        self.map = Map(map_width, map_height)
        self.num_rays = num_rays
        self.max_steps = max_steps
        self.reset()

    def _rand_free_pos(self, avoid=None):
        return self.map.find_random_empty(avoid=avoid)

    def reset(self):
        # random pick reset_default or reset_near_by
        if random.random() < 0.5:
            print("Resetting to default positions")
            return self.reset_default()
        else:
            print("Resetting to nearby positions")
            return self.reset_near_by()
        
    def reset_default(self):
        avoid = set()
        h_x, h_y = self._rand_free_pos()
        avoid.add((int(h_x), int(h_y)))
        t_x, t_y = self._rand_free_pos(avoid=avoid)
        angle1 = random.uniform(0, 2*math.pi)
        angle2 = random.uniform(0, 2*math.pi)
        self.hider = Player(h_x, h_y, angle1, PLAYER_RADIUS, 2.5, PLAYER_ROT_SPEED)
        self.hunter = Player(t_x, t_y, angle2, PLAYER_RADIUS, 2.5, PLAYER_ROT_SPEED)
        self.steps = 0
        obs_hider = self._get_obs(self.hider, self.hunter)
        obs_hunter = self._get_obs(self.hunter, self.hider)
        return obs_hider, obs_hunter
    
    def reset_near_by(self):
        avoid = set()
        h_x, h_y = self._rand_free_pos()
        avoid.add((int(h_x), int(h_y)))

        # Try to place the hunter near the hider
        def try_nearby(hx, hy):
            # neighbor offsets: (dx, dy): up, down, left, right, diagonals, etc
            neighbor_offsets = [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,-1),(-1,1),(1,1)]
            random.shuffle(neighbor_offsets)
            for dx, dy in neighbor_offsets:
                nx, ny = int(hx+dx), int(hy+dy)
                if not self.map.is_wall(nx+0.5, ny+0.5) and (nx, ny) != (int(hx), int(hy)):
                    return nx+0.5, ny+0.5
            return None

        found = try_nearby(h_x, h_y)
        if found:
            t_x, t_y = found
        else:
            # fallback to random spawn if all neighbors are blocked
            t_x, t_y = self._rand_free_pos(avoid=avoid)

        angle1 = random.uniform(0, 2*math.pi)
        angle2 = random.uniform(0, 2*math.pi)
        self.hider = Player(h_x, h_y, angle1, PLAYER_RADIUS, 2.5, PLAYER_ROT_SPEED)
        self.hunter = Player(t_x, t_y, angle2, PLAYER_RADIUS, 2.5, PLAYER_ROT_SPEED)
        self.steps = 0
        obs_hider = self._get_obs(self.hider, self.hunter)
        obs_hunter = self._get_obs(self.hunter, self.hider)
        return obs_hider, obs_hunter

    def _get_obs(self, me, other):
        assert hasattr(me, 'angle') and hasattr(other, 'angle'), f"me:{type(me)}, other:{type(other)}"
        # [distance to wall per ray, distance to other per ray]
        rays = raycast_2d(me.x, me.y, me.angle, PLAYER_FOV, self.num_rays, self.map, [other])
        wall = np.array([min(ray['distance'], RAY_MAX_DISTANCE)/RAY_MAX_DISTANCE for ray in rays])
        # for "visible" others, use normalized distance, else 1.0
        other_hits = []
        for ray in rays:
            if ray['object_hit'] is other:
                val = min(ray['object_hit_distance'], RAY_MAX_DISTANCE)/RAY_MAX_DISTANCE
            else:
                val = 1.0
            other_hits.append(val)
        other_arr = np.array(other_hits)
        ang = np.array([
            math.cos(me.angle),
            math.sin(me.angle),
            math.cos(other.angle),
            math.sin(other.angle)
        ])
        vel = np.zeros(2)   # Placeholder for velocity if you want to add it
        return np.concatenate([wall, other_arr, ang, vel])

    def step(self, action_hider, action_hunter):
        reward_hider = 0
        reward_hunter = 0
        act_map = [
            (1, 0, 0),   # move forward
            (-1, 0, 0),  # move backward
            (0, -1, 0),  # strafe left
            (0, 1, 0),   # strafe right
            (0, 0, -1),  # turn left
            (0, 0, 1),   # turn right
            (0, 0, 0),   # stay
        ]
        for act, agent in zip([action_hider, action_hunter], [self.hider, self.hunter]):
            fwd, strafe, rot = act_map[act]
            agent.move(fwd, strafe, self.map, dt=0.20)
            agent.rotate(rot, dt=0.15)
        self.steps += 1

        # Reward structure
        done = False
        dist = math.hypot(self.hider.x - self.hunter.x, self.hider.y - self.hunter.y)
        caught = dist < (self.hider.radius + self.hunter.radius) * 0.92
        if caught:
            reward_hider = -20
            reward_hunter = +20
            done = True
        elif self.max_steps == -1:
            # continue
            reward_hider = 0
            reward_hunter = 0
        elif self.steps >= self.max_steps:
            reward_hider = 5
            reward_hunter = -2
            done = True
        else:
            reward_hider = +1
            reward_hunter = -1

        # Always use Players! Never obs vectors!
        obs_hider = self._get_obs(self.hider, self.hunter)
        obs_hunter = self._get_obs(self.hunter, self.hider)
        return (obs_hider, obs_hunter), (reward_hider, reward_hunter), done

    def render(self, renderer, font, fps=None, extra=None):
        hunter_fake = FakePlayer(self.hunter.x, self.hunter.y, self.map, COLOR_FAKE_PLAYER, self.hunter.radius)
        rays_h = raycast_2d(self.hider.x, self.hider.y, self.hider.angle, PLAYER_FOV, self.num_rays, self.map, [self.hunter])
        rays_t = raycast_2d(self.hunter.x, self.hunter.y, self.hunter.angle, PLAYER_FOV, self.num_rays, self.map, [self.hider])
        renderer.draw_2d_view(self.map, self.hider, rays_h, [], hunter_fake, font, 0, fps or 0, show_full_map=True)
        rect = renderer.surface.get_rect()
        if extra:
            for i, txt in enumerate(extra.split("\n")):
                renderer.surface.blit(font.render(txt, True, (250,250,250)), (8, rect.bottom-30-17*i))