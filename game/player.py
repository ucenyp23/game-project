class Player(pygame.sprite.Sprite):
    """This class represents the player sprite"""
    def __init__(self, player_x, player_y):
        super().__init__()
        self.image = pygame.Surface((100, 20))
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.centerx = player_x
        self.rect.bottom = player_y
        self.velocity = pygame.Vector2(0, 0)
        self.player_movement_zone = pygame.Rect(640, 360, 640, 360)
        self.player_speed = 1000
        self.player_max_jumps = 2
        self.jump_counter = 0

    def update(self, delta_time):
        """Update the velocity and position of the player."""
        match self.rect.bottom:
            case player_movement_zone.bottom:
                self.velocity.y = 0
                self.jump_counter = 0
            case _:
                self.velocity.y += self.player_speed * delta_time
                self.rect.y += self.velocity.y * delta_time
        self.rect.x += self.velocity.x * delta_time
        self.rect.clamp_ip(self.player_movement_zone)

    def move(self, direction):
        """Move the player horizontally."""
        self.velocity.x = direction * self.player_speed

    def jump(self):
        """Make the player jump."""
        match self.jump_counter < self.player_max_jumps:
            case True:
                self.vel.y = -self.player_speed
                self.jump_counter += 1

    def draw(self, screen):
        """Draw the player on the screen."""
        screen.blit(self.image, self.rect)