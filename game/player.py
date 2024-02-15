class Player(pygame.sprite.Sprite):
    """This class represents the player sprite"""
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((100, 20))
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.centerx = PLAYER_X
        self.rect.bottom = PLAYER_Y
        self.velocity = pygame.Vector2(0, 0)
        self.player_movement_zone = pygame.Rect(int(SCREEN_WIDTH / 3), int(SCREEN_HEIGHT / 3), int(SCREEN_WIDTH / 3), int(SCREEN_HEIGHT / 3))
        self.gravity = GRAVITY
        self.jump_counter = 0

    def update(self, delta_time):
        """Update the velocity and position of the player."""
        match self.rect.bottom:
            case player_movement_zone.bottom:
                self.velocity.y = 0
                self.jump_counter = 0
            case _:
                self.velocity.y += self.gravity * delta_time
                self.rect.y += self.velocity.y * delta_time
        self.rect.x += self.velocity.x * delta_time
        self.rect.clamp_ip(self.player_movement_zone)

    def move(self, direction):
        """Move the player horizontally."""
        self.velocity.x = direction * PLAYER_SPEED

    def jump(self):
        """Make the player jump."""
        match self.jump_counter < PLAYER_MAX_JUMPS:
            case True:
                self.vel.y = -PLAYER_SPEED
                self.jump_counter += 1

    def draw(self, screen):
        """Draw the player on the screen."""
        screen.blit(self.image, self.rect)