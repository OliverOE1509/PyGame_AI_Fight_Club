import time
import pygame
from colors import *
from agent import Agent

class GridGame():
    
    def __init__(self, window_width, window_height, fps, sound = False):
        print("shooters")
        self.window_width = window_width
        self.window_height = window_height
        self.fps = fps

        # TODO
        self.agent = Agent(3, 10, (0,255,0), dx = 1, shoot_key = pygame.K_SPACE, player_id = 0)
        self.opponent = Agent(16,10, (0,0,255), dx=-1, shoot_key=pygame.K_RETURN)
        pygame.init()
        self.screen = pygame.display.set_mode((window_width, window_height))
        pygame.display.set_caption("AI Fight Club")
        self.colors = Colors
        self.background_color = self.colors['background']
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 24, bold=True)
        self.bullets = []

    def step(self):
        # Run the whole game in here
        for event in pygame.event.get():
            pass
        print("Running game")
        time.sleep(1)

        
    

