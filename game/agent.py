import pygame

class Agent:
    def __init__(self, x, y, color, dx, shoot_key, player_id):
        self.x = x
        self.y = y
        self.color = color
        self.bullets = []
        self.dx = dx
        self.shoot_key = shoot_key

        # timer mellom hvert skudd
        self.last_shot = 0
        self.shot_cooldown = 500  # I millisekunder. 500 = 1/2 sekunder
        self.health = 3
        self.alive = True
        self.hit_cooldown = 0
        self.hit_time = 0
        self.player_id = player_id

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
        if now - self.last_shot > self.shot_cooldown:
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