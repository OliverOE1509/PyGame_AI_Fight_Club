import gymnasium as gym
from gymnasium import spaces
import numpy as np
import time
from collections import deque
import matplotlib.pyplot as plt
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.vec_env import DummyVecEnv
import torch
import os
import pygame

# ==================== GAME CORE ====================
class AIFightClubCore:
    """Core game logic for AI Fight Club without rendering"""
    
    def __init__(self, grid_size: int = 20):
        self.grid_size = grid_size
        self.cell_size = 1
        self.reset()
    
    def reset(self) -> np.ndarray:
        """Reset the game to initial state and return initial observation"""
        # Create agents with 3 lives each
        self.agent = self._create_agent(3, 10, 1, 0)
        self.opponent = self._create_agent(16, 10, -1, 1)
        
        # Game state
        self.done = False
        self.winner = None
        self.step_count = 0
        self.last_update_time = time.time()
        
        # Game statistics
        self.agent_lives_lost = 0
        self.opponent_lives_lost = 0
        self.agent_shots_fired = 0
        self.opponent_shots_fired = 0
        
        return self._get_observation()
    
    def _create_agent(self, x: int, y: int, dx: int, player_id: int) -> dict:
        """Create an agent with the given parameters"""
        return {
            'x': x, 'y': y, 'dx': dx, 'player_id': player_id,
            'bullets': [], 'health': 3, 'alive': True,
            'last_shot': 0, 'shot_cooldown': 0.5,
            'hit_time': 0, 'hit_cooldown': 0.5,
            'score': 0
        }
    
    def step(self, agent_action: int, opponent_action: int = None) -> tuple:
        """
        Execute one game step
        
        Returns:
            observation, reward, terminated, truncated, info
        """
        current_time = time.time()
        dt = current_time - self.last_update_time
        self.last_update_time = current_time
        
        # Process actions
        self._process_action(self.agent, agent_action, dt)
        
        if opponent_action is not None:
            self._process_action(self.opponent, opponent_action, dt)
        else:
            # Default opponent behavior
            self._default_opponent_behavior(dt)
        
        # Update game state
        self._update_bullets(dt)
        self._check_collisions(current_time)
        
        # Get reward
        reward = self._get_reward()
        
        # Check if game is done
        terminated = self.done
        truncated = self.step_count > 1000  # End after 1000 steps
        
        # Get info with detailed statistics
        info = {
            'winner': self.winner,
            'agent_health': self.agent['health'],
            'opponent_health': self.opponent['health'],
            'step_count': self.step_count,
            'agent_lives_lost': self.agent_lives_lost,
            'opponent_lives_lost': self.opponent_lives_lost,
            'agent_shots_fired': self.agent_shots_fired,
            'opponent_shots_fired': self.opponent_shots_fired,
        }
        
        self.step_count += 1
        
        return self._get_observation(), reward, terminated, truncated, info
    
    def _process_action(self, agent: dict, action: int, dt: float):
        """Convert action index to game action"""
        if action == 0:  # MOVE UP
            self._move_agent(agent, -1)
        elif action == 1:  # MOVE DOWN
            self._move_agent(agent, 1)
        elif action == 2:  # SHOOT
            self._shoot_bullet(agent, dt)
            # Track shots fired
            if agent['player_id'] == 0:
                self.agent_shots_fired += 1
            else:
                self.opponent_shots_fired += 1
        # action 3: DO_NOTHING
    
    def _move_agent(self, agent: dict, dy: int):
        """Move agent vertically"""
        new_y = agent['y'] + dy
        if 0 <= new_y < self.grid_size:
            agent['y'] = new_y
    
    def _shoot_bullet(self, agent: dict, dt: float):
        """Agent shoots a bullet if cooldown has expired"""
        agent['last_shot'] += dt
        if agent['last_shot'] >= agent['shot_cooldown']:
            agent['bullets'].append({
                'x': agent['x'], 
                'y': agent['y'], 
                'dx': agent['dx'], 
                'dy': 0,
                'speed': 5.0  # cells per second
            })
            agent['last_shot'] = 0  # Reset cooldown
    
    def _default_opponent_behavior(self, dt: float):
        """Default behavior for opponent (simple tracking)"""
        # Move toward player with some randomness
        if self.opponent['y'] < self.agent['y'] and np.random.random() > 0.3:
            self._move_agent(self.opponent, 1)
        elif self.opponent['y'] > self.agent['y'] and np.random.random() > 0.3:
            self._move_agent(self.opponent, -1)
        
        # Shoot with some probability
        if np.random.random() < 0.1:  # 10% chance to shoot each frame
            self._shoot_bullet(self.opponent, dt)
    
    def _update_bullets(self, dt: float):
        """Update bullet positions and remove off-screen bullets"""
        for agent in [self.agent, self.opponent]:
            for bullet in agent['bullets'][:]:
                # Move bullet
                bullet['x'] += bullet['dx'] * bullet['speed'] * dt
                bullet['y'] += bullet['dy'] * bullet['speed'] * dt
                
                # Remove bullets that are off screen
                if not (0 <= bullet['x'] < self.grid_size and 0 <= bullet['y'] < self.grid_size):
                    agent['bullets'].remove(bullet)
    
    def _check_collisions(self, current_time: float):
        """Check for bullet collisions"""
        # Check if agent bullets hit opponent
        for bullet in self.agent['bullets'][:]:
            if self._check_bullet_hit(self.opponent, bullet, current_time):
                self.agent['bullets'].remove(bullet)
                self.agent['score'] += 1  # Reward for hitting
                if not self.opponent['alive']:
                    self.done = True
                    self.winner = self.agent['player_id']
        
        # Check if opponent bullets hit agent
        for bullet in self.opponent['bullets'][:]:
            if self._check_bullet_hit(self.agent, bullet, current_time):
                self.opponent['bullets'].remove(bullet)
                self.opponent['score'] += 1  # Opponent gets points too
                if not self.agent['alive']:
                    self.done = True
                    self.winner = self.opponent['player_id']
    
    def _check_bullet_hit(self, agent: dict, bullet: dict, current_time: float) -> bool:
        """Check if a bullet hits an agent"""
        if not agent['alive']:
            return False
            
        # Check if still in hit cooldown
        if current_time - agent['hit_time'] < agent['hit_cooldown']:
            return False
            
        # Check collision (using manhattan distance for simplicity)
        if abs(agent['x'] - bullet['x']) < 1 and abs(agent['y'] - bullet['y']) < 1:
            agent['health'] -= 1
            
            # Track lives lost
            if agent['player_id'] == 0:
                self.agent_lives_lost += 1
            else:
                self.opponent_lives_lost += 1
                
            agent['hit_time'] = current_time
            if agent['health'] <= 0:
                agent['alive'] = False
            return True
        return False
    
    def _get_observation(self) -> np.ndarray:
        """Convert game state to numerical representation for AI"""
        # Create a grid representation
        state = np.zeros((self.grid_size, self.grid_size, 4), dtype=np.float32)
        
        # Channel 0: Agent position
        if self.agent['alive']:
            y, x = int(self.agent['y']), int(self.agent['x'])
            if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
                state[y, x, 0] = 1.0
        
        # Channel 1: Opponent position
        if self.opponent['alive']:
            y, x = int(self.opponent['y']), int(self.opponent['x'])
            if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
                state[y, x, 1] = 1.0
        
        # Channel 2: Agent bullets
        for bullet in self.agent['bullets']:
            x, y = int(bullet['x']), int(bullet['y'])
            if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
                state[y, x, 2] = 1.0
        
        # Channel 3: Opponent bullets
        for bullet in self.opponent['bullets']:
            x, y = int(bullet['x']), int(bullet['y'])
            if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
                state[y, x, 3] = 1.0
        
        # Flatten and add health information
        grid_state = state.flatten()
        health_info = np.array([
            self.agent['health'] / 3.0, 
            self.opponent['health'] / 3.0
        ], dtype=np.float32)
        
        full_state = np.concatenate([grid_state, health_info])
        return full_state
    
    def _get_reward(self) -> float:
        """Calculate reward for the learning agent"""
        reward = 0.0
        
        # Small penalty for each step to encourage faster games
        reward -= 0.001
        
        # Reward for hitting opponent
        reward += self.agent['score'] * 1.0
        self.agent['score'] = 0  # Reset for next step
        
        # Penalty for getting hit
        if self.agent_lives_lost > 0:
            reward -= 0.2 * self.agent_lives_lost
            self.agent_lives_lost = 0
        
        # Large reward for winning
        if self.done and self.winner == 0:
            reward += 10.0
        
        # Large penalty for losing
        if self.done and self.winner == 1:
            reward -= 10.0
        
        return reward

# ==================== GYM ENVIRONMENT ====================
class AIFightClubEnv(gym.Env):
    """Custom Environment for AI Fight Club that follows gym interface"""
    
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
    
    def _init_render(self):
        """Initialize pygame for rendering"""
        try:
            pygame.init()
            self.cell_size = 30
            self.screen_size = self.game.grid_size * self.cell_size
            self.screen = pygame.display.set_mode((self.screen_size, self.screen_size))
            pygame.display.set_caption('AI Fight Club - Training')
            
            # Colors
            self.colors = {
                'background': (255, 255, 255),
                'grid': (200, 200, 200),
                'agent': (0, 255, 0),
                'opponent': (0, 0, 255),
                'bullet': (255, 0, 0),
                'health': (255, 0, 0)
            }
            
            self.clock = pygame.time.Clock()
        except ImportError:
            print("Pygame not installed. Running without rendering.")
            self.render_mode = None
    
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
    
    def render(self):
        """Render the environment"""
        if self.render_mode is None:
            return
        
        if self.render_mode == 'human':
            self._render_frame()
    
    def _render_frame(self):
        """Render a single frame"""
        # Clear screen
        self.screen.fill(self.colors['background'])
        
        # Draw grid
        for x in range(self.game.grid_size):
            for y in range(self.game.grid_size):
                rect = pygame.Rect(
                    x * self.cell_size, 
                    y * self.cell_size, 
                    self.cell_size, 
                    self.cell_size
                )
                pygame.draw.rect(self.screen, self.colors['grid'], rect, 1)
        
        # Draw agents
        self._draw_agent(self.game.agent, self.colors['agent'])
        self._draw_agent(self.game.opponent, self.colors['opponent'])
        
        # Draw bullets
        self._draw_bullets(self.game.agent['bullets'], self.colors['bullet'])
        self._draw_bullets(self.game.opponent['bullets'], self.colors['bullet'])
        
        # Update display
        pygame.display.flip()
        self.clock.tick(self.metadata['render_fps'])
    
    def _draw_agent(self, agent, color):
        """Draw an agent on the screen"""
        if agent['alive']:
            rect = pygame.Rect(
                agent['x'] * self.cell_size,
                agent['y'] * self.cell_size,
                self.cell_size,
                self.cell_size
            )
            pygame.draw.rect(self.screen, color, rect)
            
            # Draw health bar
            health_width = (self.cell_size * agent['health']) / 3
            health_rect = pygame.Rect(
                agent['x'] * self.cell_size,
                agent['y'] * self.cell_size - 5,
                health_width,
                3
            )
            pygame.draw.rect(self.screen, self.colors['health'], health_rect)
    
    def _draw_bullets(self, bullets, color):
        """Draw bullets on the screen"""
        for bullet in bullets:
            bullet_rect = pygame.Rect(
                bullet['x'] * self.cell_size + self.cell_size // 4,
                bullet['y'] * self.cell_size + self.cell_size // 4,
                self.cell_size // 2,
                self.cell_size // 2
            )
            pygame.draw.rect(self.screen, color, bullet_rect)
    
    def close(self):
        """Close the environment and cleanup"""
        if hasattr(self, 'screen'):
            pygame.quit()

# ==================== TRAINING CODE ====================
class TrainingCallback(BaseCallback):
    """Custom callback for tracking training metrics"""
    
    def __init__(self, check_freq=1000, verbose=1):
        super(TrainingCallback, self).__init__(verbose)
        self.check_freq = check_freq
        self.episode_rewards = []
        self.episode_lengths = []
        self.win_rates = []
        self.episode_count = 0
        self.reward_buffer = deque(maxlen=100)
        self.length_buffer = deque(maxlen=100)
        self.win_buffer = deque(maxlen=100)
        
    def _on_step(self) -> bool:
        # Log rewards and episode lengths when episodes are done
        if 'episode' in self.locals['infos'][0]:
            episode_info = self.locals['infos'][0]['episode']
            self.reward_buffer.append(episode_info['r'])
            self.length_buffer.append(episode_info['l'])
            self.win_buffer.append(1 if self.locals['infos'][0].get('winner') == 0 else 0)
            
            # Update metrics every check_freq steps
            if self.num_timesteps % self.check_freq == 0:
                avg_reward = np.mean(self.reward_buffer)
                avg_length = np.mean(self.length_buffer)
                win_rate = np.mean(self.win_buffer) * 100
                
                self.episode_rewards.append(avg_reward)
                self.episode_lengths.append(avg_length)
                self.win_rates.append(win_rate)
                
                print(f"Timestep: {self.num_timesteps}")
                print(f"Avg Reward: {avg_reward:.2f}")
                print(f"Avg Episode Length: {avg_length:.2f}")
                print(f"Win Rate: {win_rate:.2f}%")
                print("-" * 40)
                
                # Save model if it has the best win rate so far
                if win_rate >= max(self.win_rates, default=0):
                    self.model.save("best_model")
        
        return True

def create_env(render_mode=None):
    """Create and return the environment"""
    env = AIFightClubEnv(render_mode=render_mode)
    return env

def train_model(total_timesteps=1000000):
    """Train the model with progress tracking"""
    
    # Create environment
    env = create_env()
    env = DummyVecEnv([lambda: env])
    
    # Create model
    model = PPO(
        "MlpPolicy",
        env,
        verbose=1,
        learning_rate=3e-4,
        n_steps=2048,
        batch_size=64,
        n_epochs=10,
        gamma=0.99,
        gae_lambda=0.95,
        clip_range=0.2,
        ent_coef=0.01,
        tensorboard_log="./tensorboard_logs/"
    )
    
    # Create callback
    callback = TrainingCallback()
    
    # Train the model
    print("Starting training...")
    model.learn(total_timesteps=total_timesteps, callback=callback, tb_log_name="PPO")
    
    # Save the final model
    model.save("final_model")
    
    # Plot results
    plot_training_results(callback.episode_rewards, callback.episode_lengths, callback.win_rates)
    
    env.close()
    return model, callback

def plot_training_results(rewards, lengths, win_rates):
    """Plot training results"""
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 12))
    
    # Plot rewards
    ax1.plot(rewards)
    ax1.set_title('Average Reward per Episode')
    ax1.set_ylabel('Reward')
    ax1.grid(True)
    
    # Plot episode lengths
    ax2.plot(lengths)
    ax2.set_title('Average Episode Length')
    ax2.set_ylabel('Steps')
    ax2.grid(True)
    
    # Plot win rates
    ax3.plot(win_rates)
    ax3.set_title('Win Rate')
    ax3.set_ylabel('Win Rate (%)')
    ax3.set_xlabel('Evaluation Points')
    ax3.grid(True)
    
    plt.tight_layout()
    plt.savefig('training_results.png')
    plt.show()

# ==================== MAIN EXECUTION ====================
if __name__ == "__main__":
    # Install required packages if not already installed
    try:
        import stable_baselines3
    except ImportError:
        print("Installing required packages...")
        import subprocess
        subprocess.check_call(["pip", "install", "stable-baselines3", "gymnasium", "pygame"])
    
    # Train the model
    model, callback = train_model(total_timesteps=50000)
    
    # Print final results
    print("\nTraining Completed!")
    print(f"Final Average Reward: {np.mean(callback.reward_buffer):.2f}")
    print(f"Final Win Rate: {np.mean(callback.win_buffer) * 100:.2f}%")
    
    # Test the trained model
    print("\nTesting trained model...")
    test_env = AIFightClubEnv(render_mode='human')
    obs, _ = test_env.reset()
    
    for i in range(3):  # Test 3 episodes
        done = False
        while not done:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = test_env.step(action)
            done = terminated or truncated
            
            if done:
                print(f"Episode {i+1} finished. Winner: Player {info.get('winner', 'Unknown') + 1}")
                obs, _ = test_env.reset()
                break
    
    test_env.close()