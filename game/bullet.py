import pygame

class Bullet:
    def __init__(self, x, y, dx, dy):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        #self.image = pygame.transform.scale(bullet_img, (cell_size // 2, cell_size // 2))
        try:
            bullet_path = os.path.join(ASSETS_PATH, 'bullet_img.png')
            self.image = pygame.image.load(bullet_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (cell_size // 2, cell_size // 2))
        except:
            self.image = pygame.Surface((cell_size // 2, cell_size // 2), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (255, 0, 0), 
                             (cell_size // 4, cell_size // 4), 
                             cell_size // 4)
    
    def move(self):
        self.x += self.dx
        self.y += self.dy


    def draw(self):
        img_width, img_height = bullet_img.get_size()
        pos_x = self.x * cell_size + (cell_size - img_width) // 2
        pos_y = self.y * cell_size + (cell_size - img_height) // 2
        screen.blit(bullet_img, (pos_x, pos_y))

    def off_screen(self):
        '''Remove bullet if its off the screen: Save memory
        If bullets are fired left or right, change self.x <= screen width to screen height
        Else change screen_width to screen_height'''
        return not (self.x >= 0 and self.x <= screen_width)

