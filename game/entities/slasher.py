class Slasher(pygame.sprite.Sprite):
    """This class represents the player sprite"""
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((100, 20))
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y

    def update(self, delta_time):
        """Update the velocity and position of the player."""
        self.rect.y = self.player_y
        self.rect.x = self.player_x

    def draw(self, screen):
        """Draw the player on the screen."""
        screen.blit(self.image, self.rect)