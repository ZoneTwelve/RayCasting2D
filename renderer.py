# renderer.py

import pygame
import math
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, VIEW_SCALE,
    COLOR_BG, COLOR_GRID, COLOR_WALL, COLOR_FLOOR,
    COLOR_PLAYER, COLOR_PLAYER_DIR, COLOR_RAY, COLOR_RAY_HIT,
    COLOR_STATIC_SPRITE, COLOR_FAKE_PLAYER, COLOR_NPC_DIR)

def map_to_screen(mx, my):
    """Map grid coordinates to screen pixel coordinates."""
    sx = int(mx * VIEW_SCALE)
    sy = int(my * VIEW_SCALE)
    return sx, sy

class Renderer:
    def __init__(self, surface, map_width, map_height):
        self.surface = surface
        self.map_width = map_width
        self.map_height = map_height

        self.offset_x = (SCREEN_WIDTH - map_width * VIEW_SCALE)//2
        self.offset_y = (SCREEN_HEIGHT - map_height * VIEW_SCALE)//2

    def draw_2d_view(self, game_map, player, rays, static_sprites, fake_player, font, dt, fps):
        self.surface.fill(COLOR_BG)
        self.draw_grid(game_map)
        self.draw_static_sprites(static_sprites)
        self.draw_fake_player(fake_player)
        self.draw_player(player)
        self.draw_rays(player, rays)

        # FPS
        fps_surf = font.render(f"FPS: {int(fps)}", True, (230,230,230))
        self.surface.blit(fps_surf, (8, 8))

    def draw_grid(self, game_map):
        grid = game_map.get_grid()
        for y, row in enumerate(grid):
            for x, cell in enumerate(row):
                rect = pygame.Rect(
                    self.offset_x + x*VIEW_SCALE, self.offset_y + y*VIEW_SCALE,
                    VIEW_SCALE, VIEW_SCALE)
                color = COLOR_FLOOR if cell == ' ' else COLOR_WALL
                pygame.draw.rect(self.surface, color, rect)
                pygame.draw.rect(self.surface, COLOR_GRID, rect, 1)

    def draw_player(self, player):
        px, py = map_to_screen(player.x, player.y)
        px += self.offset_x
        py += self.offset_y
        radius_px = int(player.radius * VIEW_SCALE)
        # Player
        pygame.draw.circle(self.surface, COLOR_PLAYER, (px, py), radius_px)
        # Direction
        dx = int(player.radius * 2.7 * VIEW_SCALE *  math.cos(player.angle))
        dy = int(player.radius * 2.7 * VIEW_SCALE *  math.sin(player.angle))
        pygame.draw.line(
            self.surface, COLOR_PLAYER_DIR, (px, py), (px + dx, py + dy), 3)

    def draw_static_sprites(self, sprites):
        for s in sprites:
            sx, sy = map_to_screen(s.x, s.y)
            sx += self.offset_x
            sy += self.offset_y
            pygame.draw.circle(self.surface, COLOR_STATIC_SPRITE, (sx, sy), int(s.radius * VIEW_SCALE))

    def draw_fake_player(self, fake_player):
        sx, sy = map_to_screen(fake_player.x, fake_player.y)
        sx += self.offset_x
        sy += self.offset_y
        pygame.draw.circle(self.surface, COLOR_FAKE_PLAYER, (sx, sy), int(fake_player.radius * VIEW_SCALE))
        # Fake player "direction"
        ndx = int(fake_player.radius * 2.5 * VIEW_SCALE * math.cos(fake_player.target_dir))
        ndy = int(fake_player.radius * 2.5 * VIEW_SCALE * math.sin(fake_player.target_dir))
        pygame.draw.line(self.surface, COLOR_NPC_DIR, (sx, sy), (sx + ndx, sy + ndy), 2)

    def draw_rays(self, player, rays):
        px, py = map_to_screen(player.x, player.y)
        px += self.offset_x
        py += self.offset_y
        for ray in rays:
            if ray['hit'] and ray['distance'] > 0.01:
                hx, hy = map_to_screen(ray['hit_x'], ray['hit_y'])
                hx += self.offset_x
                hy += self.offset_y
                pygame.draw.line(self.surface, COLOR_RAY, (px, py), (hx, hy), 1)
                pygame.draw.circle(self.surface, COLOR_RAY_HIT, (hx, hy), 4)