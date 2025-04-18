import torch
import numpy as np
from ai_env import HiderHunterEnv
from ai_models import DQNAgent

def train(num_episodes=2, save_every=80):
    env = HiderHunterEnv(map_width=13, map_height=13, num_rays=21)
    input_dim = len(env._get_obs(env.hider, env.hunter))
    n_actions = 7
    hider = DQNAgent(input_dim, n_actions)
    hunter = DQNAgent(input_dim, n_actions)

    for ep in range(num_episodes):
        obs_h, obs_t = env.reset()
        tot_r_h = 0
        tot_r_t = 0
        for step in range(340):
            act_h = hider.select(obs_h, n_actions)
            act_t = hunter.select(obs_t, n_actions)
            (next_obs_h, next_obs_t), (r_h, r_t), done = env.step(act_h, act_t)
            hider.remember(obs_h, act_h, r_h, next_obs_h, float(done))
            hunter.remember(obs_t, act_t, r_t, next_obs_t, float(done))
            obs_h, obs_t = next_obs_h, next_obs_t
            tot_r_h += r_h
            tot_r_t += r_t
            hider.update()
            hunter.update()
            if done:
                break
        print(f"Episode {ep+1}/{num_episodes}: Hider reward={tot_r_h:.1f} Hunter reward={tot_r_t:.1f} Eps {hider.epsilon():.3f}")
        if (ep+1) % save_every == 0:
            torch.save(hider.policy.state_dict(), f"hider_dqn.pth")
            torch.save(hunter.policy.state_dict(), f"hunter_dqn.pth")
            print("Saved models.")
    torch.save(hider.policy.state_dict(), f"hider_dqn.pth")
    torch.save(hunter.policy.state_dict(), f"hunter_dqn.pth")
    print("Saved models.")

if __name__ == "__main__":
    train()