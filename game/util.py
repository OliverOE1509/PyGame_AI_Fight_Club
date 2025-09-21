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