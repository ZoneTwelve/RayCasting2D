import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random
from collections import deque

class MLP(nn.Module):
    def __init__(self, input_dim, output_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, output_dim)
        )
    def forward(self, x):
        return self.net(x)

class DQNAgent:
    def __init__(self, input_dim, output_dim, lr=1e-3, gamma=0.96):
        self.device = torch.device('mps')
        self.policy = MLP(input_dim, output_dim).to(self.device)
        self.target = MLP(input_dim, output_dim).to(self.device)
        self.target.load_state_dict(self.policy.state_dict())
        self.optimizer = optim.Adam(self.policy.parameters(), lr=lr)
        self.gamma = gamma
        self.memory = deque(maxlen=40000)
        self.batch_size = 96
        self.steps = 0
        self.sync_every = 128
        self.eps_min = 0.01
        self.eps_max = 0.9
        self.eps_decay = 7000

    def select(self, obs, act_space):
        if np.random.rand() < self.epsilon():
            return np.random.randint(act_space)
        obs = torch.tensor(obs, dtype=torch.float32, device=self.device).unsqueeze(0)
        with torch.no_grad():
            q = self.policy(obs)
            return int(torch.argmax(q).item())

    def epsilon(self):
        return max(self.eps_min, self.eps_max - self.steps / self.eps_decay)

    def remember(self, obs, act, rew, next_obs, done):
        self.memory.append((obs, act, rew, next_obs, done))

    def update(self):
        if len(self.memory) < self.batch_size:
            return
        batch = random.sample(self.memory, k=self.batch_size)
        obs, act, rew, next_obs, done = zip(*batch)
        obs = torch.tensor(np.array(obs), dtype=torch.float32, device=self.device)
        next_obs = torch.tensor(np.array(next_obs), dtype=torch.float32, device=self.device)
        act = torch.tensor(act, dtype=torch.long, device=self.device).unsqueeze(1)
        rew = torch.tensor(rew, dtype=torch.float32, device=self.device).unsqueeze(1)
        done = torch.tensor(done, dtype=torch.float32, device=self.device).unsqueeze(1)

        q = self.policy(obs).gather(1, act)
        with torch.no_grad():
            tgt = self.target(next_obs).max(1)[0].unsqueeze(1)
            target_q = rew + self.gamma * tgt * (1 - done)
        loss = nn.functional.mse_loss(q, target_q)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        self.steps += 1
        if self.steps % self.sync_every == 0:
            self.target.load_state_dict(self.policy.state_dict())