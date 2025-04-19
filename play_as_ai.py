import pygame
import torch
import numpy as np
import math
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
    ai = DQNAgent(input_dim, n_actions)
    ai.policy.load_state_dict(torch.load('hider_dqn.pth', map_location='mps'))  # Now load the hider policy!
    ai.policy.eval()

    obs_h, obs_t = env.reset()
    done = False
    total_r = 0
    renderer = Renderer(screen, env.map.width, env.map.height)

    while True:
        dt = clock.tick(60) / 1000.0
        # Human is now HUNTER
        action_t = get_action_from_keyboard()     # Human is hunter (tracker)
        action_h = ai.select(obs_h, n_actions)    # AI is hider (evader)

        (next_obs_h, next_obs_t), (r_h, r_t), done = env.step(action_h, action_t)
        obs_h, obs_t = next_obs_h, next_obs_t
        total_r += r_t    # Reward for HUNTER (you!)

        # Camera follows hunter ("your view")
        env.render(renderer, font, extra=f"Reward: {total_r : .1f}")
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