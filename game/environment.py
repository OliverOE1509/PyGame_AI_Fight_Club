import gymnasium as gym
from gymnasium import spaces
import numpy as np
from game.core import AIFightClubCore

class AIFightClubEnv(gym.Env):
    """Enhanced environment with proper episode tracking"""
    
    metadata = {'render.modes': ['human', 'rgb_array'], 'render_fps': 30}
    
    def __init__(self, render_mode=None):
        super(AIFightClubEnv, self).__init__()
        
        self.render_mode = render_mode
        self.game = AIFightClubCore()
        
        # Define action and observation space
        self.action_space = spaces.Discrete(4)  # UP, DOWN, SHOOT, NOOP
        
        # Observation space: grid state + health info
        grid_size = self.game.grid_size
        state_size = grid_size * grid_size * 4 + 2  # 4 channels + 2 health values
        self.observation_space = spaces.Box(
            low=0, high=1, 
            shape=(state_size,), 
            dtype=np.float32
        )
        
        # Episode tracking
        self.episode_reward = 0
        self.episode_length = 0
        self.episode_count = 0
        self.total_wins = 0
        
        # For rendering
        if self.render_mode == 'human':
            self._init_render()
    
    def reset(self, seed=None, options=None):
        """Reset the environment to an initial state"""
        super().reset(seed=seed)
        
        # Reset episode stats if this is a new episode
        if self.episode_length > 0:
            self.episode_count += 1
            
        self.episode_reward = 0
        self.episode_length = 0
        
        observation = self.game.reset()
        info = {
            'episode': {
                'r': self.episode_reward,
                'l': self.episode_length,
                't': 0.0
            }
        }
        
        return observation, info
    
    def step(self, action):
        """Run one timestep of the environment's dynamics"""
        observation, reward, terminated, truncated, info = self.game.step(action)
        
        # Update episode statistics
        self.episode_reward += reward
        self.episode_length += 1
        
        # Track wins
        if terminated and info.get('winner') == 0:
            self.total_wins += 1
        
        # Add episode info to the info dict
        info['episode'] = {
            'r': self.episode_reward,
            'l': self.episode_length,
            't': 0.0
        }
        
        # Add win rate to info
        info['win_rate'] = self.total_wins / max(1, self.episode_count) * 100
        
        if self.render_mode == 'human':
            self.render()
        
        return observation, reward, terminated, truncated, info
    
    # ... (rest of the environment code remains the same)