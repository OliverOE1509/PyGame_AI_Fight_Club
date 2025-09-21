import pygame
import os

ASSETS_PATH = os.path.join(os.path.dirname(__file__), 'assets')
cell_size = 30  # Should be passed from game or made configurable
grid_size = 20  # Should be passed from game or made configurable
screen = None   # Should be passed from game

class Bullet:
    def __init__(self, x, y, dx, dy, bullet_img, cell_size):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.bullet_img = bullet_img
        self.cell_size = cell_size
        
    def move(self):
        self.x += self.dx
        self.y += self.dy


    def draw(self):
        if self.bullet_img:
            img_width, img_height = self.bullet_img.get_size()
            pos_x = self.x * self.cell_size + (self.cell_size - img_width) // 2
            pos_y = self.y * self.cell_size + (self.cell_size - img_height) // 2
            screen.blit(self.bullet_img, (pos_x, pos_y))

    def off_screen(self):
        '''Remove bullet if its off the screen: Save memory
        If bullets are fired left or right, change self.x <= screen width to screen height
        Else change screen_width to screen_height'''
        return not (0 <= self.x < grid_size and 0 <= self.y < grid_size)

