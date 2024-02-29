"""This module contains a simple game using pygame."""
import pygame

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (100, 0, 100)
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
GROUND_HEIGHT = 100

class Player(pygame.sprite.Sprite):
    """This class represents the player sprite."""
    def __init__(self, position_x, position_y):
        super().__init__()
        self.player_height = 128
        self.player_width = 64
        self.image = pygame.Surface((self.player_width, self.player_height))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.centerx = position_x
        self.rect.bottom = position_y
        self.vel = pygame.Vector2(0, 0)
        self.jump_counter = 0
        self.player_speed = 1024
        self.player_max_jump = 2
        self.gravity = 32

    def update(self, delta_time):
        """Update the velocity and position of the player."""
        self.vel.y += self.gravity
        self.rect.x += self.vel.x * delta_time
        self.rect.y += self.vel.y * delta_time
        self._collisions()

    def _collisions(self):
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
        self.vel.x = direction * self.player_speed

    def jump(self):
        """Make the player jump."""
        if self.jump_counter < self.player_max_jump:
            self.vel.y = -self.player_speed
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
    while True:
        if _events(player) is False:
            break
        sprites.update(clock.get_time() / 1000)
        screen.fill(BLACK)
        sprites.draw(screen)
        pygame.display.update()
        clock.tick(60)

def _events(player):
    """Handle events."""
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a] and not keys[pygame.K_d]:
        player.move(-1)
    elif keys[pygame.K_d] and not keys[pygame.K_a]:
        player.move(1)
    else:
        player.move(0)

    if keys[pygame.K_ESCAPE]:
        return False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
            player.jump()
    return None

if __name__ == '__main__':
    main()
