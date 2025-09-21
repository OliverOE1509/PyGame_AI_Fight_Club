import gym
from gym import spaces
import numpy as np
from pygame_local import *
from typing import Optional

class GridWorldEnc(gym.Env):
    
    def __init__(self, render_mode=None):

        # Observation: positions of both agents + health
        # [agent_x, agent_y, opp_x, opp_y, agent_health, opp_health] in this order
        low  = np.array([0,0,0,0,0,0])
        high = np.array([grid_size, grid_size, grid_size, grid_size, 3, 3])
        self.observation_space = spaces.Box(low, high, dtype=np.int32)

        '''movement ∈ {0,1,2}
        shooting ∈ {0,1}'''

        # since we have 3 actions (move up, down and shoot) I put 3 in Discrete
        self.action_space = spaces.MultiDiscrete([3,2])
  
        self.agent=None
        self.opponent=None
        self.render_mode=render_mode

    def _get_obs(self):
        return {"agent": self.agent, "opponent": self.opponent}
    
    def _get_info(self):
        return {
            "distance": np.linalg.norm(self.agent - self.opponent, ord=1)
        }
    
    def reset(self, seed: Optional[int] = None, options: Optional[dict] = None):
        super().reset(seed=seed)
        self.agent = Agent(3, 10, (0,255,0), dx=1, shoot_key=None, player_id=0)
        self.opponent = Agent(16,10, (0,0,255), dx=-1, shoot_key=None, player_id=1)
        obs = self._get_obs()
        return obs, {}
    
    def step(self, action):
        # Apply chosen action for agent
        if action == 1: self.agent.move(-1)
        elif action == 2: self.agent.move(1)
        elif action == 3: self.agent.shoot()

        # Opponent could move randomly for now
        opp_action = self.action_space.sample()
        if opp_action == 1: self.opponent.move(-1)
        elif opp_action == 2: self.opponent.move(1)
        elif opp_action == 3: self.opponent.shoot()

        # Update bullets
        self.agent.update_bullets()
        self.opponent.update_bullets()

        reward = 0
        terminated = False

        # Check collisions
        for b in self.agent.bullets[:]:
            if self.opponent.check_bullet_collision(b):
                self.agent.bullets.remove(b)
                reward += 1

        for b in self.opponent.bullets[:]:
            if self.agent.check_bullet_collision(b):
                self.opponent.bullets.remove(b)
                reward -= 1

        if not self.agent.alive:
            reward -= 10
            terminated = True
        elif not self.opponent.alive:
            reward += 10
            terminated = True

        obs = self._get_obs()
        return obs, reward, terminated, False, {}

env = GridWorldEnc()
obs, _ = env.reset()
print("Initial observation:", obs)
obs, reward, done, trunc, info = env.step((2,1))  # move down + shoot
print("Step:", obs, reward, done)