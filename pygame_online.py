import pygame
import os
from network import Network

# Initialize pygame
pygame.init()

# Game constants
ASSETS_PATH = os.path.join(os.path.dirname(__file__), 'Assets')
grid_size = 20
cell_size = 30
screen_height = grid_size * cell_size
screen_width = grid_size * cell_size
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('AI Fight Club')

# Colors
colors = {
    'background': (255, 255, 255),
    'grid': (200, 200, 200),
    'agent1': (0, 255, 0),
    'agent2': (0, 0, 255),
    'bullet': (255, 0, 0),
    'text': (255, 255, 255),
    'health': (255, 0, 0)
}

class Agent:
    def __init__(self, x, y, color, dx, shoot_key, player_id):
        self.x = x
        self.y = y
        self.color = color
        self.bullets = []
        self.dx = dx
        self.shoot_key = shoot_key
        self.player_id = player_id
        self.last_shot = 0
        self.shot_cooldown = 500
        self.health = 3
        self.alive = True
        self.hit_cooldown = 0
        self.hit_time = 0

    def check_bullet_collision(self, bullet):
        if not self.alive:
            return False
            
        now = pygame.time.get_ticks()
        if now - self.hit_time < self.hit_cooldown:
            return False
            
        if (abs(self.x - bullet.x) < 1 and abs(self.y - bullet.y) < 1):
            self.health -= 1
            self.hit_time = now
            if self.health <= 0:
                self.alive = False
            return True
        return False

    def draw(self):
        # Flash when hit
        now = pygame.time.get_ticks()
        if now - self.hit_time < 200 and self.alive:
            flash_color = (255, 255, 255)  # White flash
        else:
            flash_color = self.color
            
        pygame.draw.rect(screen, flash_color, 
                        (self.x * cell_size, self.y * cell_size, cell_size, cell_size))
        
        # Draw health bar
        if self.alive:
            health_width = (cell_size * self.health) / 3
            pygame.draw.rect(screen, colors['health'],
                           (self.x * cell_size, self.y * cell_size - 10,
                            health_width, 5))
        
    def move(self, dy):
        new_y = self.y + dy
        if 0 <= new_y < grid_size:
            self.y = new_y
    
    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shot_cooldown and self.alive:
            self.bullets.append(Bullet(self.x, self.y, self.dx, 0))
            self.last_shot = now

    def update_bullets(self):
        for bullet in self.bullets[:]:
            bullet.move()
            bullet.draw()
            if bullet.off_screen():
                self.bullets.remove(bullet)

    def update_position(self, x, y):
        self.x = x
        self.y = y

class Bullet:
    def __init__(self, x, y, dx, dy):
        self.x = x
        self.y = y
        self.dx = dx * 0.5  # Slower bullets
        self.dy = dy * 0.5
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
        img_width, img_height = self.image.get_size()
        pos_x = self.x * cell_size + (cell_size - img_width) // 2
        pos_y = self.y * cell_size + (cell_size - img_height) // 2
        screen.blit(self.image, (pos_x, pos_y))

    def off_screen(self):
        return not (0 <= self.x < grid_size and 0 <= self.y < grid_size)

def draw_grid():
    for x in range(grid_size):
        for y in range(grid_size):
            rect = pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size)
            pygame.draw.rect(screen, colors['grid'], rect, 1)

def draw_help_box(screen, font):
    help_text = [
        "HOW TO PLAY:",
        "Both players:",
        "  - Move: W (Up), S (Down)",
        "  - Shoot: SPACE",
        "Press any key to continue..."
    ]
    box_width = 300
    box_height = 250
    box_x = (screen_width - box_width) // 2
    box_y = (screen_height - box_height) // 2
    
    s = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
    s.fill((50, 50, 50, 200))
    screen.blit(s, (box_x, box_y))
    
    pygame.draw.rect(screen, (255, 255, 255), (box_x, box_y, box_width, box_height), 2)
    
    text_y = box_y + 20
    for line in help_text:
        text = font.render(line, True, (255, 255, 255))
        screen.blit(text, (box_x + 20, text_y))
        text_y += 30

def draw_game_over(screen, font, winner):
    overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    
    text = font.render(f"Player {winner + 1} wins!", True, (255, 255, 0))
    text_rect = text.get_rect(center=(screen_width // 2, screen_height // 2 - 30))
    screen.blit(text, text_rect)

    restart_text = font.render("Press R to restart", True, (255, 255, 255))
    restart_rect = restart_text.get_rect(center=(screen_width // 2, screen_height // 2 + 30))
    screen.blit(restart_text, restart_rect)

def main():
    try:
        n = Network()
        player_id = n.get_player_id()
        if player_id == -1:
            print("Failed to connect to server or get player ID")
            pygame.quit()
            return
        
        # Initialize agents
        if player_id == 0:
            agent = Agent(3, 10, colors['agent1'], 1, pygame.K_SPACE, 0)
            opponent = Agent(17, 10, colors['agent2'], -1, pygame.K_RETURN, 1)
        else:
            agent = Agent(17, 10, colors['agent2'], -1, pygame.K_RETURN, 1)
            opponent = Agent(3, 10, colors['agent1'], 1, pygame.K_SPACE, 0)

        clock = pygame.time.Clock()
        font = pygame.font.SysFont('Arial', 24, bold=True)
        running = True
        show_help = True
        game_over = False
        winner = None
        last_network_time = 0
        network_delay = 100  # ms between network updates

        while running:
            current_time = pygame.time.get_ticks()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if show_help:
                        show_help = False
                    elif game_over and event.key == pygame.K_r:
                        return main()
                    elif event.key == pygame.K_ESCAPE:
                        running = False

            if game_over:
                screen.fill(colors['background'])
                draw_grid()
                agent.draw()
                opponent.draw()
                draw_game_over(screen, font, winner)
                pygame.display.flip()
                continue

            # Movement controls
            if not show_help:
                keys = pygame.key.get_pressed()
                
                # Both players use same controls now
                if keys[pygame.K_w]:
                    agent.move(-1)
                if keys[pygame.K_s]:
                    agent.move(1)
                if keys[pygame.K_SPACE]:
                    agent.shoot()

            # Network communication with throttling
            if current_time - last_network_time > network_delay:
                try:
                    pos_data = f"{agent.x},{agent.y}"
                    opponent_data = n.send(pos_data)
                    if opponent_data == "GAME_OVER":
                        game_over = True
                        winner = 1 if player_id == 0 else 0
                    elif opponent_data:
                        opp_x, opp_y = map(int, opponent_data.split(','))
                        opponent.update_position(opp_x, opp_y)
                    last_network_time = current_time
                except Exception as e:
                    print(f"Network error: {e}")
                    running = False

            # Update game state
            agent.update_bullets()
            opponent.update_bullets()

            # Check collisions
            for bullet in agent.bullets[:]:
                if opponent.check_bullet_collision(bullet):
                    agent.bullets.remove(bullet)
                    if not opponent.alive:
                        game_over = True
                        winner = agent.player_id
                        try:
                            n.send("GAME_OVER")
                        except:
                            pass
            
            for bullet in opponent.bullets[:]:
                if agent.check_bullet_collision(bullet):
                    opponent.bullets.remove(bullet)
                    if not agent.alive:
                        game_over = True
                        winner = opponent.player_id
                        try:
                            n.send("GAME_OVER")
                        except:
                            pass

            # Drawing
            screen.fill(colors['background'])
            draw_grid()
            agent.draw()
            opponent.draw()
            agent.update_bullets()
            opponent.update_bullets()

            if show_help:
                draw_help_box(screen, font)

            pygame.display.flip()
            clock.tick(30)

    except Exception as e:
        print(f"Game error: {e}")
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()