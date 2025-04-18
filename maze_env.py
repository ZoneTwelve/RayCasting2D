import numpy as np

class HiderHunterEnv:
    """A minimal 2-player maze environment.
       maze: 2D array, 0=floor, 1=wall.
    """
    def __init__(self, maze):
        self.maze = maze
        self.height, self.width = maze.shape

        self.hider_pos = None
        self.hunter_pos = None

        self.reset()

    def random_free_cell(self):
        y, x = np.where(self.maze == 0)
        idx = np.random.randint(len(x))
        return x[idx], y[idx]

    def reset(self):
        self.hider_pos = self.random_free_cell()
        while True:
            self.hunter_pos = self.random_free_cell()
            if self.hunter_pos != self.hider_pos:
                break
        self.step_count = 0
        return self.get_obs()

    def get_obs(self):
        """Returns observation tuple for hider and hunter.
        For demo, each observes own pos, other pos, delta, and wall neighborhood (3x3).
        """
        def obs(pos, opp_pos):
            px, py = pos
            opx, opy = opp_pos
            d = np.array([opx - px, opy - py]) / max(self.width, self.height)
            nhood = self.maze[max(py-1,0):py+2, max(px-1,0):px+2].flatten()
            pad = np.zeros(9 - len(nhood))
            nhood = np.pad(nhood, (0, 9-len(nhood)), 'constant', constant_values=1)
            return np.concatenate([np.array([px/self.width, py/self.height]), d, nhood])
        hider_obs = obs(self.hider_pos, self.hunter_pos)
        hunter_obs = obs(self.hunter_pos, self.hider_pos)
        return hider_obs, hunter_obs

    def step(self, hider_action, hunter_action):
        """advance both agents by their actions (int: 0..7);  returns (obs, reward_hider, reward_hunter, done)"""
        # Move Hider
        self.hider_pos = self._attempt_move(self.hider_pos, hider_action)
        # If collision now, hunter catches
        if self.hider_pos == self.hunter_pos:
            reward_hider = -1.0
            reward_hunter = +1.0
            done = True
            return self.get_obs(), reward_hider, reward_hunter, done
        # Move Hunter
        self.hunter_pos = self._attempt_move(self.hunter_pos, hunter_action)
        # If collision now, hunter catches
        if self.hider_pos == self.hunter_pos:
            reward_hider = -1.0
            reward_hunter = +1.0
            done = True
            return self.get_obs(), reward_hider, reward_hunter, done
        # Not caught; small reward for survival
        reward_hider = +0.01
        reward_hunter = -0.01
        self.step_count += 1
        done = self.step_count > 200   # Max steps per episode
        return self.get_obs(), reward_hider, reward_hunter, done

    def _attempt_move(self, pos, action):
        from nn_agents import action_to_delta
        dx, dy = action_to_delta(action)
        nx, ny = pos[0] + dx, pos[1] + dy
        if 0 <= nx < self.width and 0 <= ny < self.height and self.maze[ny, nx] == 0:
            return (nx, ny)
        return pos # If can't move, stay