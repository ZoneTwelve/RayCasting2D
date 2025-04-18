# raycaster.py

import math
from settings import RAY_MAX_DISTANCE, RAY_STEP_SIZE

def raycast_2d(player_x, player_y, player_angle, fov, num_rays, game_map):
    """
    Returns a list of dicts:
      [{'hit': True/False, 'hit_x': float, 'hit_y': float, 'distance': float, 'ray_angle': float}]
    """
    half_fov = fov / 2
    start_angle = player_angle - half_fov
    step = fov / max(num_rays - 1, 1)
    result = []
    for i in range(num_rays):
        ray_a = start_angle + (i * step)
        res = single_ray(player_x, player_y, ray_a, game_map)
        res['ray_angle'] = ray_a
        result.append(res)
    return result

def single_ray(x0, y0, angle, game_map):
    # DDA algorithm, walks through grid
    sin_a = math.sin(angle)
    cos_a = math.cos(angle)
    x, y = x0, y0
    distance = 0.0
    max_dist = RAY_MAX_DISTANCE
    hit = False
    while distance <= max_dist:
        xi, yi = int(x), int(y)
        if game_map.is_wall(x, y):
            hit = True
            break
        x += cos_a * RAY_STEP_SIZE
        y += sin_a * RAY_STEP_SIZE
        distance += RAY_STEP_SIZE
    if hit:
        return {
            'hit': True,
            'hit_x': x,
            'hit_y': y,
            'distance': distance,
        }
    else:
        return {
            'hit': False,
            'hit_x': x,
            'hit_y': y,
            'distance': distance,
        }