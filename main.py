"""This module contains a simple game using pygame."""
import pygame

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (100, 0, 100)
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
PLAYER_WIDTH = 32
PLAYER_HEIGHT = 128
PLAYER_SPEED = 1024
PLAYER_MAX_JUMPS = 2
GROUND_HEIGHT = 100

class Player(pygame.sprite.Sprite):
    """This class represents the player sprite."""
    def __init__(self, position_x, position_y):
        super().__init__()
        self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.centerx = position_x
        self.rect.bottom = position_y
        self.vel = pygame.Vector2(0, 0)
        self.acc = pygame.Vector2(0, 0)
        self.jump_counter = 0

    def update(self, delta_time):
        """Update the velocity and position of the player."""
        self.vel.y += PLAYER_SPEED * delta_time
        self.rect.x += self.vel.x * delta_time
        self.rect.y += self.vel.y * delta_time
        self._check_collisions()

    def _check_collisions(self):
        """Check for collisions with the screen boundaries."""
        self.rect.left = max(self.rect.left, 0)
        self.rect.right = min(self.rect.right, SCREEN_WIDTH)
        self.rect.top = max(self.rect.top, 0)
        if self.rect.bottom > SCREEN_HEIGHT - GROUND_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT - GROUND_HEIGHT
            self.vel.y = 0
            self.jump_counter = 0

    def move(self, direction):
        """Move the player horizontally."""
        self.vel.x = direction * PLAYER_SPEED

    def jump(self):
        """Make the player jump."""
        if self.jump_counter < PLAYER_MAX_JUMPS:
            self.vel.y = -PLAYER_SPEED
            self.jump_timer = PLAYER_SPEED
            self.jump_counter += 1

    def draw(self, screen):
        """Draw the player on the screen."""
        screen.blit(self.image, self.rect)

def main():
    """Main function for the game."""
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Game')
    clock = pygame.time.Clock()

    sprites = pygame.sprite.Group()

    player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - GROUND_HEIGHT)
    sprites.add(player)

    ground = pygame.sprite.Sprite()
    ground.image = pygame.Surface((SCREEN_WIDTH, GROUND_HEIGHT))
    ground.image.fill(PURPLE)
    ground.rect = ground.image.get_rect()
    ground.rect.bottom = SCREEN_HEIGHT
    sprites.add(ground)

    _game_loop(sprites, screen, clock, player)

    pygame.quit()

def _game_loop(sprites, screen, clock, player):
    """Main game loop."""
    running = True
    while running:
        match _events(player):
            case False:
                break
        sprites.update(clock.get_time() / 1000)
        screen.fill(BLACK)
        sprites.draw(screen)
        pygame.display.update()
        clock.tick(60)

def _events(player):
    """Handle events."""
    for event in pygame.event.get():
        match event.type:
            case pygame.QUIT:
                return False
            case pygame.KEYUP:
                match event.key:
                    case pygame.K_a | pygame.K_d:
                        player.move(0)
            case pygame.KEYDOWN:
                match event.key:
                    case pygame.K_ESCAPE:
                        return False
                    case pygame.K_SPACE:
                        player.jump()
                    case pygame.K_a:
                        player.move(-1)
                    case pygame.K_d:
                        player.move(1)

match __name__:
    case '__main__':
        main()
