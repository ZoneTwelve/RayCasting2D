# sprite_object.py

class SpriteObject:
    def __init__(self, x, y, color, radius=0.18):
        self.x = x
        self.y = y
        self.color = color
        self.radius = radius  # For 2D

    def get_pos(self):
        return (self.x, self.y)