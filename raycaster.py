# raycaster.py

import math
from settings import RAY_MAX_DISTANCE, RAY_STEP_SIZE

def raycast_2d(player_x, player_y, player_angle, fov, num_rays, game_map, objects=[]):
    """
    Returns a list of dicts:
      [{'hit': True/False, 'hit_x': float, 'hit_y': float, 'distance': float, 'ray_angle': float,
        'object_hit': object or None,
        'object_hit_x': float (if hit),
        'object_hit_y': float (if hit),
        'object_hit_distance': float (if hit),
      }]
    objects: list, each must have .x, .y, .radius
    """
    half_fov = fov / 2
    start_angle = player_angle - half_fov
    step = fov / max(num_rays - 1, 1)
    result = []
    for i in range(num_rays):
        ray_a = start_angle + (i * step)
        res = single_ray(player_x, player_y, ray_a, game_map, objects)
        res['ray_angle'] = ray_a
        result.append(res)
    return result

def single_ray(x0, y0, angle, game_map, objects):
    sin_a = math.sin(angle)
    cos_a = math.cos(angle)
    x = x0
    y = y0
    distance = 0.0
    max_dist = RAY_MAX_DISTANCE
    hit_wall = False
    object_hit = None
    object_hit_distance = float('inf')
    object_hit_x = None
    object_hit_y = None

    # Find the first object hit (if any), and the wall hit.
    while distance <= max_dist:
        xi, yi = int(x), int(y)
        # Check objects (if any), but only if not too close (skip self-hit)
        for obj in objects:
            dx = obj.x - x
            dy = obj.y - y
            obj_dist2 = dx*dx + dy*dy
            if obj_dist2 < obj.radius * obj.radius:
                if distance < object_hit_distance:
                    object_hit = obj
                    object_hit_distance = distance
                    object_hit_x = x
                    object_hit_y = y
        # Wall check
        if game_map.is_wall(x, y):
            hit_wall = True
            break
        x += cos_a * RAY_STEP_SIZE
        y += sin_a * RAY_STEP_SIZE
        distance += RAY_STEP_SIZE

    if hit_wall:
        wall_result = {
            'hit': True,
            'hit_x': x,
            'hit_y': y,
            'distance': distance,
        }
    else:
        wall_result = {
            'hit': False,
            'hit_x': x,
            'hit_y': y,
            'distance': distance,
        }
    wall_result['object_hit'] = object_hit
    wall_result['object_hit_distance'] = object_hit_distance if object_hit is not None else None
    wall_result['object_hit_x'] = object_hit_x
    wall_result['object_hit_y'] = object_hit_y
    return wall_result