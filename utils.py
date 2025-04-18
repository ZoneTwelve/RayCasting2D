# utils.py

import math

def clamp(val, minval, maxval):
    return max(min(val, maxval), minval)

def dist(x0, y0, x1, y1):
    return math.hypot(x0 - x1, y0 - y1)

def radians_lerp(a, b, t):
    """Interpolate between angles a and b (both in radians) correctly."""
    delta = ((b - a + math.pi) % (2 * math.pi)) - math.pi
    return a + delta * t

def grid_snap(x, y):
    """Return integer grid coords for a floating-point position."""
    return int(x), int(y)