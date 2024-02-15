class Impaler(pygame.sprite.Sprite):
    """This class represents the player sprite"""
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((100, 20))
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.velocity = pygame.Vector2(0, 0)

    def update(self, delta_time):
        """Update the velocity and position of the player."""
        self.rect.y += self.velocity.y * delta_time
        self.rect.x += self.velocity.x * delta_time

    def draw(self, screen):
        """Draw the player on the screen."""
        screen.blit(self.image, self.rect)