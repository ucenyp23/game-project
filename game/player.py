class Player(pygame.sprite.Sprite):
    """This class represents the player sprite"""
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((100, 20))
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.centerx = PLAYER_X
        self.rect.bottom = PLAYER_Y
        self.vel = pygame.Vector2(0, 0)
        self.gravity = GRAVITY
        self.jump_counter = 0

    def update(self, delta_time):
        """Update the velocity and position of the player."""
        self.vel.y += self.gravity * delta_time
        self.rect.x += self.vel.x * delta_time
        self.rect.y += self.vel.y * delta_time
        self._collision()

    def _collision(self):
        """Check for collisions with the screen boundaries."""        
        self.rect.clamp_ip(pygame.Rect(SCREEN_WIDTH * (2/3), SCREEN_HEIGHT * (2/3), SCREEN_WIDTH / 3, SCREEN_HEIGHT / 3))
        
        match self.rect.bottom:
            case BOTTOM_BOUND:
                self.vel.y = 0
                self.jump_counter = 0

    def move(self, direction):
        """Move the player horizontally."""
        self.vel.x = direction * PLAYER_SPEED

    def jump(self):
        """Make the player jump."""
        match self.jump_counter < PLAYER_MAX_JUMPS:
            case True:
                self.vel.y = -PLAYER_SPEED
                self.jump_counter += 1

    def draw(self, screen):
        """Draw the player on the screen."""
        screen.blit(self.image, self.rect)