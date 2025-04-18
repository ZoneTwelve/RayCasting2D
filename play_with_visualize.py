import numpy as np
import pygame
import torch
from maze_env import HiderHunterEnv
from nn_agents import SimplePolicyNet, valid_moves

# ----------------------------------
# Parameters
# ----------------------------------
CELL_SIZE = 48
MAZE_PADDING = 2
AGENT_RADIUS = 14
FPS = 8

COLOR_BG = (30, 30, 30)
COLOR_WALL = (45, 40, 60)
COLOR_FLOOR = (180, 180, 185)
COLOR_GRID = (120, 120, 130)
COLOR_HIDER = (255, 220, 40)
COLOR_HUNTER = (246, 144, 255)
COLOR_PATH = (100, 200, 175)
COLOR_CATCH = (255, 80, 80)

# ----------------------------------
# Maze (same as training or customize)
# ----------------------------------
def make_small_maze(w, h):
    maze = np.ones((h, w), dtype=np.int32)
    maze[1:-1,1:-1] = 0
    maze[3:5, 2:7] = 1
    return maze

maze = make_small_maze(10,10)
env = HiderHunterEnv(maze)
obs_size = len(env.get_obs()[0])
n_actions = 8

# ----------------------------------
# Load Models
# ----------------------------------
hider_net = SimplePolicyNet(obs_size, n_actions)
hunter_net = SimplePolicyNet(obs_size, n_actions)
hider_net.load_state_dict(torch.load("hider_net.pt"))
hunter_net.load_state_dict(torch.load("hunter_net.pt"))
hider_net.eval()
hunter_net.eval()

# ----------------------------------
def select_action(net, obs, maze, pos):
    obs_t = torch.tensor(obs, dtype=torch.float32)
    logits = net(obs_t)
    mask = valid_moves(pos, maze)
    logits = torch.where(torch.tensor(mask, dtype=torch.bool), logits, torch.full_like(logits, -1e9))
    dist = torch.distributions.Categorical(logits=logits)
    action = dist.sample()
    return action.item()

# ----------------------------------
# Visualization functions
# ----------------------------------
def draw_maze(surface, maze):
    h, w = maze.shape
    for y in range(h):
        for x in range(w):
            rect = pygame.Rect(
                MAZE_PADDING + x*CELL_SIZE, MAZE_PADDING + y*CELL_SIZE,
                CELL_SIZE, CELL_SIZE
            )
            color = COLOR_FLOOR if maze[y, x] == 0 else COLOR_WALL
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, COLOR_GRID, rect, 1)

def map_to_screen(x, y):
    sx = MAZE_PADDING + x*CELL_SIZE + CELL_SIZE//2
    sy = MAZE_PADDING + y*CELL_SIZE + CELL_SIZE//2
    return sx, sy

def draw_agent(surface, pos, color, label=""):
    sx, sy = map_to_screen(*pos)
    pygame.draw.circle(surface, color, (sx, sy), AGENT_RADIUS)
    if label:
        font = pygame.font.SysFont("consolas", 16)
        img = font.render(label, True, (24,24,24))
        rect = img.get_rect(center=(sx, sy))
        surface.blit(img, rect)

def draw_path(surface, path, color):
    for (x, y) in path:
        sx, sy = map_to_screen(x, y)
        pygame.draw.circle(surface, color, (sx, sy), 6, 1)

# ----------------------------------
# Main loop
# ----------------------------------
def main():
    pygame.init()
    w, h = maze.shape[1], maze.shape[0]
    screen = pygame.display.set_mode((w*CELL_SIZE+2*MAZE_PADDING, h*CELL_SIZE+2*MAZE_PADDING))
    pygame.display.set_caption("AI Hider (yellow) vs Hunter (magenta)")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 20)

    # For optional trailing paths
    hider_trail = []
    hunter_trail = []

    episode = 0
    while True:
        obs = env.reset()
        hider_trail.clear()
        hunter_trail.clear()
        done = False
        t = 0

        while not done and t < 200:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            hider_obs, hunter_obs = obs
            hider_action = select_action(hider_net, hider_obs, env.maze, env.hider_pos)
            hunter_action = select_action(hunter_net, hunter_obs, env.maze, env.hunter_pos)
            obs2, r_hider, r_hunter, done = env.step(hider_action, hunter_action)
            hider_trail.append(env.hider_pos)
            hunter_trail.append(env.hunter_pos)

            # --- Draw ---
            screen.fill(COLOR_BG)
            draw_maze(screen, maze)
            draw_path(screen, hider_trail, COLOR_PATH)
            draw_agent(screen, env.hider_pos, COLOR_HIDER, "H")
            draw_agent(screen, env.hunter_pos, COLOR_HUNTER, "C")
            if done:
                sx, sy = map_to_screen(*env.hider_pos)
                pygame.draw.circle(screen, COLOR_CATCH, (sx, sy), AGENT_RADIUS+10, 3)
            caption = f"Episode {episode}, Step {t}"
            img = font.render(caption, True, (220,220,220))
            screen.blit(img, (6,3))
            pygame.display.flip()
            clock.tick(FPS)
            obs = obs2
            t += 1

        episode += 1

if __name__ == "__main__":
    main()