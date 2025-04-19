import torch
import numpy as np
from ai_env import HiderHunterEnv
from ai_models import DQNAgent

def simple_hider_policy(obs, n_actions):
    # Replace this with DQN hider for advanced scenario if desired!
    return np.random.randint(n_actions)

def train_hunter(num_episodes=1500, save_every=100):
    env = HiderHunterEnv(map_width=13, map_height=13, num_rays=21)
    input_dim = len(env._get_obs(env.hider, env.hunter))
    n_actions = 7
    hunter = DQNAgent(input_dim, n_actions)

    for ep in range(num_episodes):
        obs_h, obs_t = env.reset()
        tot_r = 0
        for step in range(340):
            action_h = simple_hider_policy(obs_h, n_actions)
            action_t = hunter.select(obs_t, n_actions)
            (next_obs_h, next_obs_t), (r_h, r_t), done = env.step(action_h, action_t)
            hunter.remember(obs_t, action_t, r_t, next_obs_t, float(done))
            obs_h, obs_t = next_obs_h, next_obs_t
            tot_r += r_t
            hunter.update()
            if done:
                break
        print(f"[HunterTrain] Ep {ep+1}/{num_episodes}: HunterReward={tot_r:.1f}  Eps={hunter.epsilon():.3f}")
        if (ep+1) % save_every == 0:
            torch.save(hunter.policy.state_dict(), f'hunter_dqn.pth')
            print("Saved hunter model.")
    torch.save(hunter.policy.state_dict(), f'hunter_dqn.pth')
    print("Saved hunter model.")

if __name__ == "__main__":
    train_hunter()