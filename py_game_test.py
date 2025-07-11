import pygame, time
import os


ASSETS_PATH = os.path.join(os.path.dirname(__file__), 'Assets')
pygame.init()
grid_size = 20
cell_size = 30
screen_height = grid_size * cell_size
screen_width = grid_size * cell_size
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('AI Fight Club')
colors = {
    'background': (255, 255, 255), # white
    'grid': (200, 200, 200), # black
    'agent1': (0, 255, 0), # green
    'agent2': (0, 0, 255), # blue
    'bullet': (255, 0, 0) # 'red
}

class Agent:
    def __init__(self, x, y, color, dx, shoot_key):
        self.x = x
        self.y = y
        self.color = color
        self.bullets = []
        self.dx = dx
        self.shoot_key = shoot_key

        # timer mellom hvert skudd
        self.last_shot = 0
        self.shot_cooldown = 500  # I millisekunder. 500 = 1/2 sekunder

    def draw(self):
        pygame.draw.rect(screen, self.color, 
                         (self.x * cell_size, self.y * cell_size, cell_size, cell_size))
        
    def move(self, dy):
        new_y = self.y + dy
        if 0 <= new_y < grid_size:
            self.y = new_y
    
    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shot_cooldown:
            self.bullets.append(Bullet(self.x, self.y, self.dx, 0))
            self.last_shot = now

    def update_bullets(self):
        for bullet in self.bullets[:]:
            bullet.move()
            bullet.draw()
            if bullet.off_screen():
                self.bullets.remove(bullet)


class Bullet:
    def __init__(self, x, y, dx, dy):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.image = pygame.transform.scale(bullet_img, (cell_size // 2, cell_size // 2))
    
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


def draw_grid():
    for x in range(grid_size):
        for y in range(grid_size):
            rect = pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size)
            pygame.draw.rect(screen, colors['grid'], rect, 1)

def draw_help_box(screen, font):
    """Draws a semi-transparent box with game instructions."""
    help_text = [
        "HOW TO PLAY:",
        "Player 1 (Green):",
        "  - Move: W (Up), S (Down)",
        "  - Shoot: SPACE",
        "Player 2 (Blue):",
        "  - Move: UP, DOWN arrows",
        "  - Shoot: ENTER",
        "",
        "Press any key to continue..."
    ]
    
    # Box dimensions and position
    box_width = 300
    box_height = 250
    box_x = (screen_width - box_width) // 2
    box_y = (screen_height - box_height) // 2
    
    # Semi-transparent background
    s = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
    s.fill((50, 50, 50, 200))  # Dark gray with transparency
    screen.blit(s, (box_x, box_y))
    
    # Draw border
    pygame.draw.rect(screen, (255, 255, 255), (box_x, box_y, box_width, box_height), 2)
    
    # Render text
    text_y = box_y + 20
    for line in help_text:
        text = font.render(line, True, (255, 255, 255))
        screen.blit(text, (box_x + 20, text_y))
        text_y += 30

def main():
    global bullet_img
    try:
        bullet_path = os.path.join(ASSETS_PATH, 'bullet_img.png')
        bullet_img = pygame.image.load(bullet_path).convert_alpha()
        # Scale to appropriate size (about 1/2 to 2/3 of cell_size works well)
        #bullet_img = pygame.transform.scale(bullet_img, (cell_size // 2, cell_size // 2))
    except Exception as e:
        bullet_image = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
        pygame.draw.circle(bullet_image, (255, 0, 0), 
                          (cell_size // 4, cell_size // 4), 
                          cell_size // 4)

    clock = pygame.time.Clock()
    font = pygame.font.SysFont('Arial', 20)
    agent1 = Agent(3, 10, colors['agent1'], dx = 1, shoot_key = pygame.K_SPACE)
    agent2 = Agent(16, 10, colors['agent2'], dx = -1, shoot_key = pygame.K_RETURN)
    bullets = []
    
    running = True
    FPS = 60
    previous_time = pygame.time.get_ticks()
    dt = 0
    timer = 0
    record = 0
    passed, start = False, False
    show_help = True
    help_time = 0
    #print(previous_time)

    #player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)

    while running:
        #print(previous_time)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and show_help:
                show_help = False


        now = time.time()
        dt = now - previous_time
        now = previous_time

        if not show_help:
            keys = pygame.key.get_pressed()

            # agent 1
            if keys[pygame.K_w]:
                agent1.move(-1)
            if keys[pygame.K_s]:
                agent1.move(1)
            if keys[agent1.shoot_key]:
                agent1.shoot()

            # agent 2
            if keys[pygame.K_UP]:
                agent2.move(-1)
            if keys[pygame.K_DOWN]:
                agent2.move(1)
            if keys[agent2.shoot_key]:
                agent2.shoot()
        
        
    
        screen.fill(colors['background'])
        draw_grid()
        agent1.draw()
        agent2.draw()
        agent1.update_bullets()
        agent2.update_bullets()

        if show_help:
            if help_time == 0:
                help_time = pygame.time.get_ticks()
            draw_help_box(screen, font)

        ##start_time = pygame.time.get_ticks()
        #daw_instruction_box(start_time)

        pygame.display.flip()
        clock.tick(20)

    #pygame.draw.circle(screen, 'red', player_pos, 40)

    #keys = pygame.key.get_pressed()
    #if keys[pygame.K_w]:
    #    player_pos.y -= 300 * dt
    #if keys[pygame.K_s]:
    #    player_pos.y += 300 * dt
    #if keys[pygame.K_a]:
    #    player_pos.x -= 300 * dt
    #if keys[pygame.K_d]:
    #    player_pos.x += 300 * dt
    #pygame.display.flip()
    #dt = clock.tick(1000) / 1000

    pygame.quit()

if __name__ == "__main__":
    main()