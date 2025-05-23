# renderer.py

import pygame
import math
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, VIEW_SCALE,
    COLOR_BG, COLOR_WALL, COLOR_GRID, COLOR_FLOOR,
    COLOR_PLAYER, COLOR_PLAYER_DIR, COLOR_RAY, COLOR_RAY_HIT,
    COLOR_STATIC_SPRITE, COLOR_FAKE_PLAYER, COLOR_NPC_DIR)

def map_to_screen(mx, my, player):
    """
    Converts a map coordinate (mx, my) to a screen coordinate,
    centering the camera on the player's position.
    """
    sx = int((mx - player.x) * VIEW_SCALE + SCREEN_WIDTH // 2)
    sy = int((my - player.y) * VIEW_SCALE + SCREEN_HEIGHT // 2)
    return sx, sy

class Renderer:
    def __init__(self, surface, map_width, map_height):
        self.surface = surface
        self.map_width = map_width
        self.map_height = map_height

    def draw_2d_view(self, game_map, player, rays, static_sprites, fake_player, font, dt, fps, show_full_map=False):
        self.surface.fill(COLOR_BG)
        if show_full_map:
            self.draw_full_map(game_map, player, rays, static_sprites, fake_player)
        else:
            self.draw_rays_and_hits(player, rays)
            self.draw_visible_objects_by_ray(rays, static_sprites, fake_player, player)
            self.draw_player(player)
        # FPS
        fps_surf = font.render(f"FPS: {int(fps)}", True, (230,230,230))
        self.surface.blit(fps_surf, (8, 8))

    def draw_full_map(self, game_map, player, rays, static_sprites, fake_player):
        self.draw_grid(game_map, player)
        self.draw_all_sprites(static_sprites, player)
        self.draw_fake_player(fake_player, player)
        self.draw_player(player)
        self.draw_all_rays(player, rays)

    def draw_grid(self, game_map, player):
        grid = game_map.get_grid()
        for y, row in enumerate(grid):
            for x, cell in enumerate(row):
                # Draw each cell at its map location
                sx, sy = map_to_screen(x + 0.5, y + 0.5, player)
                rect = pygame.Rect(
                    sx - VIEW_SCALE//2, sy - VIEW_SCALE//2, VIEW_SCALE, VIEW_SCALE)
                color = COLOR_FLOOR if cell == ' ' else COLOR_WALL
                pygame.draw.rect(self.surface, color, rect)
                pygame.draw.rect(self.surface, COLOR_GRID, rect, 1)

    def draw_player(self, player):
        px, py = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        radius_px = int(player.radius * VIEW_SCALE)
        pygame.draw.circle(self.surface, COLOR_PLAYER, (px, py), radius_px)
        dx = int(player.radius * 2.7 * VIEW_SCALE *  math.cos(player.angle))
        dy = int(player.radius * 2.7 * VIEW_SCALE *  math.sin(player.angle))
        pygame.draw.line(self.surface, COLOR_PLAYER_DIR, (px, py), (px + dx, py + dy), 3)

    def draw_all_sprites(self, sprites, player):
        for s in sprites:
            sx, sy = map_to_screen(s.x, s.y, player)
            pygame.draw.circle(self.surface, COLOR_STATIC_SPRITE, (sx, sy), int(s.radius * VIEW_SCALE))

    def draw_fake_player(self, fake_player, player):
        sx, sy = map_to_screen(fake_player.x, fake_player.y, player)
        pygame.draw.circle(self.surface, COLOR_FAKE_PLAYER, (sx, sy), int(fake_player.radius * VIEW_SCALE))
        ndx = int(fake_player.radius * 2.5 * VIEW_SCALE * math.cos(fake_player.target_dir))
        ndy = int(fake_player.radius * 2.5 * VIEW_SCALE * math.sin(fake_player.target_dir))
        pygame.draw.line(self.surface, COLOR_NPC_DIR, (sx, sy), (sx + ndx, sy + ndy), 2)

    def draw_rays_and_hits(self, player, rays):
        px, py = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        for ray in rays:
            xend, yend = None, None
            # Draw up to first hit (object or wall, whichever closer)
            if ray['object_hit'] is not None and (not ray['hit'] or ray['object_hit_distance'] < ray['distance']):
                xend, yend = ray['object_hit_x'], ray['object_hit_y']
            elif ray['hit']:
                xend, yend = ray['hit_x'], ray['hit_y']
            if xend is not None and yend is not None:
                hx, hy = map_to_screen(xend, yend, player)
                pygame.draw.line(self.surface, COLOR_RAY, (px, py), (hx, hy), 1)
            # Wall hit marker
            if ray['hit']:
                hx, hy = map_to_screen(ray['hit_x'], ray['hit_y'], player)
                pygame.draw.circle(self.surface, COLOR_RAY_HIT, (hx, hy), 5)
            # Object hit marker
            if ray['object_hit'] is not None and (not ray['hit'] or ray['object_hit_distance'] < ray['distance']):
                ox, oy = map_to_screen(ray['object_hit_x'], ray['object_hit_y'], player)
                color = get_obj_color(ray['object_hit'])
                pygame.draw.circle(self.surface, color, (ox, oy), int(ray['object_hit'].radius * VIEW_SCALE)+2)

    def draw_visible_objects_by_ray(self, rays, sprites, fake_player, player):
        # For each object, if any ray's object_hit is this object, show it.
        visible_sprites = set()
        visible_fake_player = False
        for ray in rays:
            obj = ray.get('object_hit')
            if obj is None:
                continue
            if obj is fake_player:
                visible_fake_player = True
            else:
                visible_sprites.add(obj)
        # Draw sprites
        for obj in visible_sprites:
            sx, sy = map_to_screen(obj.x, obj.y, player)
            pygame.draw.circle(self.surface, COLOR_STATIC_SPRITE, (sx, sy), int(obj.radius * VIEW_SCALE))
        # Draw fake player
        if visible_fake_player:
            fx, fy = map_to_screen(fake_player.x, fake_player.y, player)
            pygame.draw.circle(self.surface, COLOR_FAKE_PLAYER, (fx, fy), int(fake_player.radius * VIEW_SCALE))
            ndx = int(fake_player.radius * 2.5 * VIEW_SCALE * math.cos(fake_player.target_dir))
            ndy = int(fake_player.radius * 2.5 * VIEW_SCALE * math.sin(fake_player.target_dir))
            pygame.draw.line(self.surface, COLOR_NPC_DIR, (fx, fy), (fx + ndx, fy + ndy), 2)

    def draw_all_rays(self, player, rays):
        px, py = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        for ray in rays:
            xend, yend = None, None
            if ray['object_hit'] is not None and (not ray['hit'] or ray['object_hit_distance'] < ray['distance']):
                xend, yend = ray['object_hit_x'], ray['object_hit_y']
            elif ray['hit']:
                xend, yend = ray['hit_x'], ray['hit_y']
            if xend is not None and yend is not None:
                hx, hy = map_to_screen(xend, yend, player)
                pygame.draw.line(self.surface, COLOR_RAY, (px, py), (hx, hy), 1)
            if ray['hit']:
                hx, hy = map_to_screen(ray['hit_x'], ray['hit_y'], player)
                pygame.draw.circle(self.surface, COLOR_RAY_HIT, (hx, hy), 5)
            if ray['object_hit'] is not None and (not ray['hit'] or ray['object_hit_distance'] < ray['distance']):
                ox, oy = map_to_screen(ray['object_hit_x'], ray['object_hit_y'], player)
                color = get_obj_color(ray['object_hit'])
                pygame.draw.circle(self.surface, color, (ox, oy), int(ray['object_hit'].radius * VIEW_SCALE)+2)

def get_obj_color(obj):
    from settings import COLOR_STATIC_SPRITE, COLOR_FAKE_PLAYER
    if hasattr(obj, '__class__') and obj.__class__.__name__ == 'FakePlayer':
        return COLOR_FAKE_PLAYER
    return COLOR_STATIC_SPRITE