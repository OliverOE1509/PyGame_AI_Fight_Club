import time
import pygame
from colors import Colors
import numpy as np
from agent import Agent
from bullet import Bullet

class GridGame():
    
    def __init__(self, grid_size = 20, cell_size = 30, render=False):
        self.grid_size = grid_size
        self.cell_size = cell_size
        self.render = render
        self.colors = Colors

        # TODO
        self.agent = Agent(3, 10, Colors['agent1'], dx = 1, player_id = 0)
        self.opponent = Agent(16,10, (0,0,255), dx=-1, player_id = 1)
        self.done = False
        self.winner = None
        self.step_count = 0

        if self.render:
            self._init_pygame()

    def _init_pygame(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.grid_size * self.cell_size,
                                              self.grid_size * self.cell_size))
        pygame.display.set_caption("AI Fight CLub")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24, bold = True)

    def _load_bullet_image(self):
        try:
            import os
            asset_path = os.path.join(os.path.dirname(__file__), 'assets')
            bullet_path = os.path.join(asset_path, 'bullet_img.png')
            bullet_img = pygame.image.load(bullet_path).convert_alpha()
            return pygame.transform.scale(bullet_img, (self.cell_size // 2, self.cell_size // 2))
        except:
            bullet_surface = pygame.Surface((self.cell_size // 2, self.cell_size // 2), pygame.SRCALPHA)
            pygame.draw.circle(bullet_surface, Colors['bullet'], 
                               (self.cell_size // 4, self.cell_size // 4),
                               self.cell_size // 4)
            return bullet_surface

    def reset(self):
        """Reset the game to initial state"""
        self.agent = Agent(3, 10, self.colors.agent1, dx=1, player_id=0)
        self.opponent = Agent(16, 10, self.colors.agent2, dx=-1, player_id=1)
        self.done = False
        self.winner = None
        self.step_count = 0
        return self._get_state()
    
    def step(self, agent_action, opponent_action=None):
        """
        Execute one game step
        
        Args:
            agent_action: Action for the learning agent (0-3)
            opponent_action: Action for the opponent (if None, use scripted policy)
            
        Returns:
            state, reward, done, info
        """
        # Process actions
        self._process_action(self.agent, agent_action)
        
        if opponent_action is not None:
            self._process_action(self.opponent, opponent_action)
        else:
            # Default opponent behavior
            self._default_opponent_behavior()
        
        # Update game state
        self._update_bullets()
        self._check_collisions()
        
        # Get reward
        reward = self._get_reward()
        
        # Check if game is done
        done = self.done
        
        # Render if enabled
        if self.render:
            self._render()
        
        self.step_count += 1
        
        return self._get_state(), reward, done, {'winner': self.winner}
    
    def _process_action(self, agent, action):
        """Convert action index to game action"""
        if action == 0:  # MOVE UP
            agent.move(-1, self.grid_size)
        elif action == 1:  # MOVE DOWN
            agent.move(1, self.grid_size)
        elif action == 2:  # SHOOT
            agent.shoot(self.bullet_img, self.cell_size)
        # action 3: DO_NOTHING
    
    def _default_opponent_behavior(self):
        """Default behavior for opponent (simple tracking)"""
        if self.opponent.y < self.agent.y:
            self.opponent.move(1, self.grid_size)
        elif self.opponent.y > self.agent.y:
            self.opponent.move(-1, self.grid_size)
        elif pygame.time.get_ticks() - self.opponent.last_shot > self.opponent.shot_cooldown:
            self.opponent.shoot(self.bullet_img, self.cell_size)
    
    def _update_bullets(self):
        """Update bullet positions"""
        self.agent.update_bullets(self.screen if self.render else None)
        self.opponent.update_bullets(self.screen if self.render else None)
    
    def _check_collisions(self):
        """Check for bullet collisions"""
        # Check if agent bullets hit opponent
        for bullet in self.agent.bullets[:]:
            if self.opponent.check_bullet_collision(bullet):
                self.agent.bullets.remove(bullet)
                if not self.opponent.alive:
                    self.done = True
                    self.winner = self.agent.player_id
        
        # Check if opponent bullets hit agent
        for bullet in self.opponent.bullets[:]:
            if self.agent.check_bullet_collision(bullet):
                self.opponent.bullets.remove(bullet)
                if not self.agent.alive:
                    self.done = True
                    self.winner = self.opponent.player_id
    
    def _get_state(self):
        """Convert game state to numerical representation for AI"""
        # Create a grid representation
        state = np.zeros((self.grid_size, self.grid_size, 4), dtype=np.float32)
        
        # Channel 0: Agent position
        if self.agent.alive:
            state[self.agent.y, self.agent.x, 0] = 1.0
        
        # Channel 1: Opponent position
        if self.opponent.alive:
            state[self.opponent.y, self.opponent.x, 1] = 1.0
        
        # Channel 2: Agent bullets
        for bullet in self.agent.bullets:
            x, y = int(bullet.x), int(bullet.y)
            if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
                state[y, x, 2] = 1.0
        
        # Channel 3: Opponent bullets
        for bullet in self.opponent.bullets:
            x, y = int(bullet.x), int(bullet.y)
            if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
                state[y, x, 3] = 1.0
        
        # Flatten and add health information
        grid_state = state.flatten()
        health_info = np.array([
            self.agent.health / 3.0, 
            self.opponent.health / 3.0
        ])
        
        full_state = np.concatenate([grid_state, health_info])
        return full_state
    
    def _get_reward(self):
        """Calculate reward for the learning agent"""
        reward = 0
        
        # Small penalty for each step to encourage faster games
        reward -= 0.01
        
        # Large reward for winning
        if self.done and self.winner == 0:  # Agent won
            reward += 10
        
        # Large penalty for losing
        if self.done and self.winner == 1:  # Agent lost
            reward -= 10
        
        return reward
    
    def _render(self):
        """Render the game state"""
        if not self.render:
            return
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.done = True
        
        # Draw background
        self.screen.fill(self.colors.background)
        
        # Draw grid
        for x in range(self.grid_size):
            for y in range(self.grid_size):
                rect = pygame.Rect(x * self.cell_size, y * self.cell_size, 
                                 self.cell_size, self.cell_size)
                pygame.draw.rect(self.screen, self.colors.grid, rect, 1)
        
        # Draw agents and bullets
        self.agent.draw(self.screen, self.cell_size, self.colors.__dict__)
        self.opponent.draw(self.screen, self.cell_size, self.colors.__dict__)
        self._update_bullets()  # This also draws bullets
        
        # Update display
        pygame.display.flip()
        self.clock.tick(30)
    
    def close(self):
        """Clean up resources"""
        if self.render:
            pygame.quit()
        
    

