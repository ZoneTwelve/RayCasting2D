import numpy as np
import torch
import torch.optim as optim

from maze_env import HiderHunterEnv
from nn_agents import SimplePolicyNet, valid_moves

def make_small_maze(w, h):
    # Simple open maze; 1=wall, 0=floor
    maze = np.ones((h, w), dtype=np.int32)
    maze[1:-1,1:-1] = 0  # Hollow box
    maze[3:5, 2:7] = 1   # Interior wall chunk
    return maze

maze = make_small_maze(10,10)
env = HiderHunterEnv(maze)

obs_size = len(env.get_obs()[0])
n_actions = 8

hider_net = SimplePolicyNet(obs_size, n_actions)
hunter_net = SimplePolicyNet(obs_size, n_actions)
optim_hider = optim.Adam(hider_net.parameters(), lr=1e-3)
optim_hunter = optim.Adam(hunter_net.parameters(), lr=1e-3)

def select_action(net, obs, maze, pos):
    obs_t = torch.tensor(obs, dtype=torch.float32)
    logits = net(obs_t)
    mask = valid_moves(pos, maze)
    logits = torch.where(torch.tensor(mask, dtype=torch.bool), logits, torch.full_like(logits, -1e9))
    dist = torch.distributions.Categorical(logits=logits)
    action = dist.sample()
    return action.item(), dist.log_prob(action)

def discount_rewards(rewards, gamma=0.99):
    """Simple reward-to-go for reinforce"""
    res = []
    acc = 0
    for r in reversed(rewards):
        acc = r + gamma * acc
        res.append(acc)
    return list(reversed(res))

max_episodes = 500
for episode in range(max_episodes):
    obs = env.reset()
    hider_logp, hider_rewards = [], []
    hunter_logp, hunter_rewards = [], []
    done = False
    while not done:
        hider_obs, hunter_obs = obs
        hider_action, hider_lprob = select_action(hider_net, hider_obs, env.maze, env.hider_pos)
        hunter_action, hunter_lprob = select_action(hunter_net, hunter_obs, env.maze, env.hunter_pos)
        obs2, r_hider, r_hunter, done = env.step(hider_action, hunter_action)
        hider_logp.append(hider_lprob)
        hunter_logp.append(hunter_lprob)
        hider_rewards.append(r_hider)
        hunter_rewards.append(r_hunter)
        obs = obs2

    # Compute losses (REINFORCE/vanilla policy gradient)
    hider_returns = discount_rewards(hider_rewards, gamma=0.98)
    hunter_returns = discount_rewards(hunter_rewards, gamma=0.98)
    hider_loss = -torch.stack([lp * ret for lp, ret in zip(hider_logp, hider_returns)]).sum()
    hunter_loss = -torch.stack([lp * ret for lp, ret in zip(hunter_logp, hunter_returns)]).sum()

    optim_hider.zero_grad()
    hider_loss.backward()
    optim_hider.step()
    optim_hunter.zero_grad()
    hunter_loss.backward()
    optim_hunter.step()

    if episode % 100 == 0:
        print(f"Episode {episode}: Hider return {sum(hider_rewards):.2f} | Hunter return {sum(hunter_rewards):.2f}")

# After training, save both models
torch.save(hider_net.state_dict(), "hider_net.pt")
torch.save(hunter_net.state_dict(), "hunter_net.pt")