import pygame
import torch
import numpy as np
from ai_env import HiderHunterEnv
from ai_models import DQNAgent
from settings import *
from renderer import Renderer

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    font = pygame.font.SysFont('consolas', 21)
    clock = pygame.time.Clock()

    env = HiderHunterEnv(map_width=17, map_height=17, num_rays=21)
    input_dim = len(env._get_obs(env.hider, env.hunter))
    n_actions = 7
    # AI is hider, load hider weights (or use random policy line if no model)
    ai = DQNAgent(input_dim, n_actions)
    try:
        ai.policy.load_state_dict(torch.load('hider_dqn.pth', map_location='mps'))
        ai.policy.eval()
        def hider_policy(obs, n_actions): return ai.select(obs, n_actions)
    except Exception:
        print('No hider_dqn.pth found, using random hider!')
        def hider_policy(obs, n_actions): return np.random.randint(n_actions)

    obs_h, obs_t = env.reset()
    done = False
    total_r = 0
    renderer = Renderer(screen, env.map.width, env.map.height)

    while True:
        dt = clock.tick(60) / 1000.0
        # Hunter: YOU (keyboard), Hider: AI/random
        action_t = get_action_from_keyboard()
        action_h = hider_policy(obs_h, n_actions)
        (next_obs_h, next_obs_t), (r_h, r_t), done = env.step(action_h, action_t)
        obs_h, obs_t = next_obs_h, next_obs_t
        total_r += r_t  # Hunter's reward

        # Render with camera and player at hunter position
        # (By default env.render focuses on self.hider, to switch, draw manually)
        rays_t = env.num_rays
        from fake_player import FakePlayer
        hunter_fake = FakePlayer(env.hunter.x, env.hunter.y, env.map, COLOR_FAKE_PLAYER, env.hunter.radius)
        rays = env.hunter  # Player obj
        renderer.draw_2d_view(
            env.map, env.hunter,   # Camera/player is hunter!
            # Optional: for pure camera, can set to [] but showing rays is useful
            # Below: rays for hunter, objects: draw hider as "sprite"
            raycast_obs(env.hunter, env.hider, env),  # Rays for hunter towards hider
            [env.hider], hunter_fake, font, 0, 0,
            show_full_map=True)
        rect = renderer.surface.get_rect()
        renderer.surface.blit(font.render(f"Reward: {total_r:.1f}", True, (250,250,250)), (8, rect.bottom-30))
        pygame.display.flip()
        if done:
            pygame.time.wait(700)
            obs_h, obs_t = env.reset()
            total_r = 0
            done = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                import sys
                sys.exit()

def raycast_obs(me, other, env):
    from raycaster import raycast_2d
    return raycast_2d(me.x, me.y, me.angle, PLAYER_FOV, env.num_rays, env.map, [other])

def get_action_from_keyboard():
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] or keys[pygame.K_UP]: return 0
    if keys[pygame.K_s] or keys[pygame.K_DOWN]: return 1
    if keys[pygame.K_a]: return 2
    if keys[pygame.K_d]: return 3
    if keys[pygame.K_LEFT]: return 4
    if keys[pygame.K_RIGHT]: return 5
    return 6

if __name__ == "__main__":
    main()