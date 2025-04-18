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

    # Player initial position & angle
    px, py = game_map.get_start_pos()
    p_angle = math.radians(35)
    player = Player(
        px, py, p_angle,
        PLAYER_RADIUS, PLAYER_MOVE_SPEED, PLAYER_ROT_SPEED)

    # Static sprites (collectibles or objects)
    num_sprites = max(2, (MAP_WIDTH * MAP_HEIGHT) // 45)
    used = set()
    used.add((int(px), int(py)))
    static_sprites = []
    for _ in range(num_sprites):
        sx, sy = game_map.find_random_empty(avoid=used)
        used.add((int(sx), int(sy)))
        static_sprites.append(SpriteObject(sx, sy, COLOR_STATIC_SPRITE))

    # FakePlayer (wandering NPC)
    fx, fy = game_map.find_random_empty(avoid=used)
    fake_player = FakePlayer(fx, fy, game_map, COLOR_FAKE_PLAYER)

    # Renderer
    renderer = Renderer(screen, MAP_WIDTH, MAP_HEIGHT)

    # --- Game Loop ---
    while True:
        dt = clock.tick(FPS) / 1000.0  # Delta time in seconds
        fps = clock.get_fps()
        handle_events(player, game_map, dt)
        fake_player.update(dt)  # Update NPC

        # Raycasting (per frame)
        rays = raycast_2d(
            player.x, player.y, player.angle,
            PLAYER_FOV, NUM_RAYS, game_map)

        # Draw
        renderer.draw_2d_view(
            game_map, player, rays,
            static_sprites, fake_player, font, dt, fps)
        pygame.display.flip()


def handle_events(player, game_map, dt):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
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
    # (AD = strafe; Left/Right = turn)
    player.move(forward, strafe, game_map, dt)
    player.rotate(rot, dt)

if __name__ == "__main__":
    main()