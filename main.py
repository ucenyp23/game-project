"""This module contains a simple game using pygame."""
import random
import pygame

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

class Player(pygame.sprite.Sprite):
    """This class represents the player sprite."""
    def __init__(self, position_x, position_y):
        super().__init__()
        self.player_height = 32
        self.player_width = 32
        self.image = pygame.Surface((self.player_width, self.player_height))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.centerx = position_x
        self.rect.bottom = position_y
        self.vel = pygame.Vector2(0, 0)
        self.jump_counter = 0
        self.player_speed = 64
        self.player_max_jump = 2
        self.gravity = 8

    def update(self, delta_time, layout):
        """Update the velocity and position of the player."""
        self.rect.x += self.vel.x * delta_time
        self.rect.y += self.vel.y * delta_time
        self._collisions(layout)

    def _collisions(self, layout):
        """Check for collisions with the screen boundaries."""
        tile_width = tile_height = 64
        for y, row in enumerate(layout):
            for x, tile in enumerate(row):
                if tile == '#':
                    tile_rect = pygame.Rect(x*tile_width, y*tile_height, tile_width, tile_height)
                    if self.rect.colliderect(tile_rect):
                        if self.rect.bottom - tile_rect.top < 8 and self.rect.bottom - tile_rect.top > -1:
                            self.rect.bottom = tile_rect.top
                            self.vel.y = 0
                            self.jump_counter = 0
                        elif self.rect.top - tile_rect.bottom > -8 and self.rect.top - tile_rect.bottom > 1:
                            self.rect.top = tile_rect.bottom
                        else:
                            self.vel.y += self.gravity

                        if self.rect.right - tile_rect.left < 8 and self.rect.right - tile_rect.left > -1:
                            self.rect.right = tile_rect.left
                        elif self.rect.left - tile_rect.right > -8 and self.rect.left - tile_rect.right > 1:
                            self.rect.left = tile_rect.right

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

def _generate_map():
    width, height = 17, 17
    width_5 = width // 5
    width_2_5 = width * 2 // 5
    width_3_5 = width * 3 // 5
    width_4_5 = width * 4 // 5
    width_1, height_1 = width - 1, height - 1
    avoid_chars = {'P', '1', '2', '3'}

    def _generate():
        layout = [['#' if i % 2 == 0 or j in {0, width_1} or i in {0, height_1} else ' ' for j in range(width)] for i in range(height)]
        for i in range(1, height_1):
            if i % 2 == 0:
                rand_range = random.randrange(1, width_5)
                for _ in range(rand_range):
                    clime = random.randrange(1, width_1)
                    if layout[i - 1][clime] == ' ':
                        layout[i][clime] = ' '
            else:
                ml, mr = sorted(random.randrange(width_2_5, width_3_5) for _ in range(2))
                rand_range_start = random.randrange(1, width_5)
                rand_range_end = random.randrange(width_4_5, width)
                for j in list(range(rand_range_start)) + list(range(rand_range_end, width_1)) + list(range(ml, mr)):
                    if layout[i - 1][j] == '#':
                        layout[i][j] = '#'
        return layout

    def _validate(height, width, layout):
        visited = set()
        start = next((i, j) for i in range(height) for j in range(width) if layout[i][j] == ' ')

        stack = [start]
        while stack:
            i, j = stack.pop()
            if (i, j) not in visited:
                visited.add((i, j))
                for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    ni, nj = i + di, j + dj
                    if 0 <= ni < height and 0 <= nj < width and layout[ni][nj] == ' ':
                        stack.append((ni, nj))

        return all(layout[i][j] != ' ' or (i, j) in visited for i in range(height) for j in range(width))

    layout = _generate()
    while not _validate(height, width, layout):
        layout = _generate()

    player = next((i, j) for i in range(height_1, 0, -1) for j in range(width) if layout[i][j] == ' ' and layout[i][j + 1] == ' ')
    layout[player[0]][player[1]] = 'P'

    for _ in range(random.randrange(5, 8)):
        while True:
            i, j = random.randrange(0, width), random.randrange(0, height)
            if layout[i][j] == ' ' and layout[i + 1][j] == '#' and layout[i][j - 1] not in avoid_chars and layout[i][j + 1] not in avoid_chars:
                layout[i][j] = random.choice(['1', '2', '3'])
                break

    return layout

def main():
    """Main function for the game."""
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Game')
    clock = pygame.time.Clock()

    sprites = pygame.sprite.Group()

    layout = _generate_map()

    for y, row in enumerate(layout):
        for x, tile in enumerate(row):
            if tile == 'P':
                player = Player((x + 0.5)*64, (y + 1)*64)
    sprites.add(player)

    _game_loop(sprites, screen, clock, player, layout)

    pygame.quit()

def _game_loop(sprites, screen, clock, player, layout):
    """Main game loop."""
    while True:
        if _events(player) is False:
            break
        sprites.update(clock.get_time() / 1000, layout)
        screen.fill(BLACK)
        tile_width = tile_height = 64
        for y, row in enumerate(layout):
            for x, tile in enumerate(row):
                if tile == '#':
                    tile = pygame.Rect(x*tile_width, y*tile_height, tile_width, tile_height)
                    pygame.draw.rect(screen, WHITE, tile)
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
