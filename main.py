# main.py

import sys
import math
import random
import pygame

from settings import *
from map import Map
from player import Player
from raycaster import raycast_2d
from utils import clamp
from sprite_object import SpriteObject
from fake_player import FakePlayer
from renderer import Renderer

def main():
    pygame.init()
    pygame.display.set_caption("2D Raycasting Visualization (Top-Down)")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    font = pygame.font.SysFont(FONT_NAME, FONT_SIZE)

    # --- Map and Entities ---
    game_map = Map(MAP_WIDTH, MAP_HEIGHT)
    px, py = game_map.get_start_pos()
    p_angle = math.radians(35)
    player = Player(
        px, py, p_angle,
        PLAYER_RADIUS, PLAYER_MOVE_SPEED, PLAYER_ROT_SPEED)
    num_sprites = max(2, (MAP_WIDTH * MAP_HEIGHT) // 45)
    used = set()
    used.add((int(px), int(py)))
    static_sprites = []
    for _ in range(num_sprites):
        sx, sy = game_map.find_random_empty(avoid=used)
        used.add((int(sx), int(sy)))
        static_sprites.append(SpriteObject(sx, sy, COLOR_STATIC_SPRITE))
    fx, fy = game_map.find_random_empty(avoid=used)
    fake_player = FakePlayer(fx, fy, game_map, COLOR_FAKE_PLAYER)
    renderer = Renderer(screen, MAP_WIDTH, MAP_HEIGHT)

    show_map = False  # Toggle flag

    while True:
        dt = clock.tick(FPS) / 1000.0
        fps = clock.get_fps()
        show_map = handle_events(player, game_map, dt, show_map)
        fake_player.update(dt)
        rays = raycast_2d(
            player.x, player.y, player.angle,
            PLAYER_FOV, NUM_RAYS, game_map)
        renderer.draw_2d_view(
            game_map, player, rays,
            static_sprites, fake_player, font, dt, fps,
            show_full_map=show_map)
        pygame.display.flip()

def handle_events(player, game_map, dt, show_map):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                show_map = not show_map
    keys = pygame.key.get_pressed()
    forward = 0
    strafe = 0
    rot = 0
    if keys[pygame.K_w] or keys[pygame.K_UP]:
        forward += 1
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        forward -= 1
    if keys[pygame.K_a]:
        strafe -= 1
    if keys[pygame.K_d]:
        strafe += 1
    if keys[pygame.K_LEFT]:
        rot -= 1
    if keys[pygame.K_RIGHT]:
        rot += 1
    player.move(forward, strafe, game_map, dt)
    player.rotate(rot, dt)
    return show_map

if __name__ == "__main__":
    main()