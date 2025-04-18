import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np

class SimplePolicyNet(nn.Module):
    """Given observation, outputs action logits."""
    def __init__(self, obs_size, n_actions, hidden=128):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(obs_size, hidden),
            nn.ReLU(),
            nn.Linear(hidden, hidden),
            nn.ReLU(),
            nn.Linear(hidden, n_actions)
        )

    def forward(self, obs):
        return self.net(obs)


# Utility functions for agent action (8 directions: one-hot discrete)
ACTIONS = [(-1,0), (1,0), (0,-1), (0,1), (-1,-1), (-1,1), (1,-1), (1,1)]  # N,S,W,E,NW,NE,SW,SE

def action_to_delta(a):
    return ACTIONS[a]

def valid_moves(pos, maze):
    """Returns a binary mask of all valid moves from pos (x,y)."""
    mask = []
    for dx, dy in ACTIONS:
        nx, ny = pos[0]+dx, pos[1]+dy
        if 0 <= nx < maze.shape[1] and 0 <= ny < maze.shape[0] and maze[ny, nx] == 0:
            mask.append(1)
        else:
            mask.append(0)
    return np.array(mask)