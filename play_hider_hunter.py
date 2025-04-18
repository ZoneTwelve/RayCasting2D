import torch
from maze_env import HiderHunterEnv
from nn_agents import SimplePolicyNet, valid_moves
import numpy as np
import time

def discount_rewards(rewards, gamma=0.99):
    res = []
    acc = 0
    for r in reversed(rewards):
        acc = r + gamma * acc
        res.append(acc)
    return list(reversed(res))

def make_small_maze(w, h):
    maze = np.ones((h, w), dtype=np.int32)
    maze[1:-1,1:-1] = 0
    maze[3:5, 2:7] = 1
    return maze

maze = make_small_maze(10,10)
env = HiderHunterEnv(maze)

obs_size = len(env.get_obs()[0])
n_actions = 8

hider_net = SimplePolicyNet(obs_size, n_actions)
hunter_net = SimplePolicyNet(obs_size, n_actions)

# Load trained weights
hider_net.load_state_dict(torch.load("hider_net.pt"))
hunter_net.load_state_dict(torch.load("hunter_net.pt"))

hider_net.eval()
hunter_net.eval()

def select_action(net, obs, maze, pos):
    obs_t = torch.tensor(obs, dtype=torch.float32)
    logits = net(obs_t)
    mask = valid_moves(pos, maze)
    logits = torch.where(torch.tensor(mask, dtype=torch.bool), logits, torch.full_like(logits, -1e9))
    dist = torch.distributions.Categorical(logits=logits)
    action = dist.sample()
    return action.item()

for episode in range(10):
    obs = env.reset()
    done = False
    t = 0
    print(f"\n--- Episode {episode} ---")
    while not done and t < 200:
        hider_obs, hunter_obs = obs
        hider_action = select_action(hider_net, hider_obs, env.maze, env.hider_pos)
        hunter_action = select_action(hunter_net, hunter_obs, env.maze, env.hunter_pos)
        obs2, r_hider, r_hunter, done = env.step(hider_action, hunter_action)
        # Print positions
        print(f"Step {t}: Hider at {env.hider_pos}, Hunter at {env.hunter_pos}")
        time.sleep(0.15)
        obs = obs2
        t += 1
    print("Done!")