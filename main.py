"""This module contains a simple game using pygame."""
# Make this code more funcional and pythonic, clean up it up and make it conform to PEP8.
import random
import pygame
import heapq

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
TILE_SIZE = 256
MAP_SIZE = 17

class Player(pygame.sprite.Sprite):
    """Player sprite class."""
    def __init__(self, position_x, position_y):
        super().__init__()
        self.image = pygame.Surface((64, 128))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.centerx = position_x
        self.rect.bottom = position_y
        self.vel = pygame.Vector2(0, 0)
        self.jump_counter = 0
        self.speed = 1024
        self.max_jump = 2
        self.gravity = 16
        self.hp = 1024
        self.sword_image = pygame.Surface((64, 32))
        self.sword_image.fill(BLUE)
        self.sword_rect = self.sword_image.get_rect()

    def update(self, delta_time, layout, player):
        """Player update function."""
        self.rect.x += self.vel.x * delta_time
        self._collisions(layout, 'x')
        self.rect.y += self.vel.y * delta_time
        self._collisions(layout, 'y')
        self.sword_rect.x = self.rect.centerx
        self.sword_rect.y = self.rect.centery

    def _collisions(self, layout, direction):
        collision = False
        for y, row in enumerate(layout):
            for x, tile in enumerate(row):
                if tile == '#':
                    tile_rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    if self.rect.colliderect(tile_rect):
                        collision = True
                        self._handle_collision(tile_rect, direction)
        if not collision and direction == 'y':
            self.vel.y += self.gravity

    def _handle_collision(self, tile_rect, direction):
        if direction == 'x':
            if self.rect.right - tile_rect.left < TILE_SIZE // 2:
                self.rect.right = tile_rect.left
                self.vel.x = 0
            elif self.rect.left - tile_rect.right > -TILE_SIZE // 2:
                self.rect.left = tile_rect.right
                self.vel.x = 0
        elif direction == 'y':
            if self.rect.bottom - tile_rect.top < TILE_SIZE // 2:
                self.rect.bottom = tile_rect.top
                self.vel.y = 0
                self.jump_counter = 0
            elif self.rect.top - tile_rect.bottom > -TILE_SIZE // 2:
                self.rect.top = tile_rect.bottom
                self.vel.y = self.gravity

    def move(self, direction):
        """Player move function."""
        self.vel.x = direction * self.speed

    def jump(self):
        """Player jump function."""
        if self.jump_counter < self.max_jump:
            self.vel.y = -self.speed
            self.jump_counter += 1

    def draw(self, screen):
        """Player draw function."""
        screen.blit(self.image, self.rect)
        screen.blit(self.sword_image, self.sword_rect)

class Kamikaze(pygame.sprite.Sprite):
    """Kamikaze sprite class."""
    def __init__(self, position_x, position_y):
        super().__init__()
        self.image = pygame.Surface((32, 32))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.centerx = position_x
        self.rect.bottom = position_y
        self.vel = pygame.Vector2(0, 0)
        self.speed = 2048
        self.hp = 64
        self.enable = False

    def move(self, player, layout):
        """Move towards the player."""
        for y, row in enumerate(layout):
            for x, tile in enumerate(row):
                if tile == '#':
                    tile_rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    if not tile_rect.clipline((self.rect.centerx, self.rect.centery), (player.rect.centerx, player.rect.centery)) and \
                        -500 < player.rect.centerx - self.rect.centerx > 500 and \
                        -500 < player.rect.centery - self.rect.centery > 500:
                        direction = pygame.Vector2((player.rect.centerx - self.rect.centerx) / 500, (player.rect.centery - self.rect.centery) / 500)
                        self.vel = direction * self.speed

    def enabling(self, player):
        """Enable movement."""
        direction = pygame.Vector2(player.rect.x - self.rect.x, (player.rect.y + player.rect.height // 2) - self.rect.y)
        within_screen = -TILE_SIZE*3 < direction.x < TILE_SIZE*3 and -TILE_SIZE*0.9 < direction.y < TILE_SIZE*0.9

        if within_screen:
            self.enable = True

    def update(self, delta_time, layout, player):
        """Kamikaze update function."""
        if player.rect.colliderect(self.rect):
            player.hp -= self.hp
            self.hp = 0
        if self.enable == False:
            self.enabling(player)
        else:
            self.move(player, layout)
        self.rect.x += self.vel.x * delta_time
        self._collisions(layout, 'x')
        self.rect.y += self.vel.y * delta_time
        self._collisions(layout, 'y')

    def _collisions(self, layout, direction):
        for y, row in enumerate(layout):
            for x, tile in enumerate(row):
                if tile == '#':
                    tile_rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    if self.rect.colliderect(tile_rect):
                        self._handle_collision(tile_rect, direction)

    def _handle_collision(self, tile_rect, direction):
        if direction == 'x':
            if self.rect.right - tile_rect.left < TILE_SIZE // 2:
                self.rect.right = tile_rect.left
                self.vel.x = 0
            elif self.rect.left - tile_rect.right > -TILE_SIZE // 2:
                self.rect.left = tile_rect.right
                self.vel.x = 0
        elif direction == 'y':
            if self.rect.bottom - tile_rect.top < TILE_SIZE // 2:
                self.rect.bottom = tile_rect.top
                self.vel.y = 0
            elif self.rect.top - tile_rect.bottom > -TILE_SIZE // 2:
                self.rect.top = tile_rect.bottom
                self.vel.y = 0

    def draw(self, screen):
        """Kamikaze draw function."""
        screen.blit(self.image, self.rect)

class Slasher(pygame.sprite.Sprite):
    """Slasher sprite class."""
    def __init__(self, position_x, position_y):
        super().__init__()
        self.image = pygame.Surface((64, 128))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.centerx = position_x
        self.rect.bottom = position_y
        self.vel = pygame.Vector2(0, 0)
        self.speed = 8192
        self.hp = 128

    def update(self, delta_time, layout, player):
        """Slasher update function."""
        self.rect.x += self.vel.x * delta_time
        self._collisions(layout, 'x')
        self.rect.y += self.vel.y * delta_time
        self._collisions(layout, 'y')

    def _collisions(self, layout, direction):
        for y, row in enumerate(layout):
            for x, tile in enumerate(row):
                if tile == '#':
                    tile_rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    if self.rect.colliderect(tile_rect):
                        self._handle_collision(tile_rect, direction)

    def _handle_collision(self, tile_rect, direction):
        if direction == 'x':
            if self.rect.right - tile_rect.left < TILE_SIZE // 2:
                self.rect.right = tile_rect.left
                self.vel.x = 0
            elif self.rect.left - tile_rect.right > -TILE_SIZE // 2:
                self.rect.left = tile_rect.right
                self.vel.x = 0
        elif direction == 'y':
            if self.rect.bottom - tile_rect.top < TILE_SIZE // 2:
                self.rect.bottom = tile_rect.top
                self.vel.y = 0
            elif self.rect.top - tile_rect.bottom > -TILE_SIZE // 2:
                self.rect.top = tile_rect.bottom
                self.vel.y = 0

    def draw(self, screen):
        """Slasher draw function."""
        screen.blit(self.image, self.rect)

class Lancer(pygame.sprite.Sprite):
    """Lancer sprite class."""
    def __init__(self, position_x, position_y):
        super().__init__()
        self.image = pygame.Surface((64, 128))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.centerx = position_x
        self.rect.bottom = position_y
        self.vel = pygame.Vector2(0, 0)
        self.speed = 8192
        self.hp = 128

    def update(self, delta_time, layout, player):
        """Lancer update function."""
        self.rect.x += self.vel.x * delta_time
        self._collisions(layout, 'x')
        self.rect.y += self.vel.y * delta_time
        self._collisions(layout, 'y')

    def _collisions(self, layout, direction):
        for y, row in enumerate(layout):
            for x, tile in enumerate(row):
                if tile == '#':
                    tile_rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    if self.rect.colliderect(tile_rect):
                        self._handle_collision(tile_rect, direction)

    def _handle_collision(self, tile_rect, direction):
        if direction == 'x':
            if self.rect.right - tile_rect.left < TILE_SIZE // 2:
                self.rect.right = tile_rect.left
                self.vel.x = 0
            elif self.rect.left - tile_rect.right > -TILE_SIZE // 2:
                self.rect.left = tile_rect.right
                self.vel.x = 0
        elif direction == 'y':
            if self.rect.bottom - tile_rect.top < TILE_SIZE // 2:
                self.rect.bottom = tile_rect.top
                self.vel.y = 0
            elif self.rect.top - tile_rect.bottom > -TILE_SIZE // 2:
                self.rect.top = tile_rect.bottom
                self.vel.y = 0

    def draw(self, screen):
        """Lancer draw function."""
        screen.blit(self.image, self.rect)

class Scarecrow(pygame.sprite.Sprite):
    """Scarecrow sprite class."""
    def __init__(self, position_x, position_y):
        super().__init__()
        self.height = 32
        self.width = 32
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.centerx = position_x
        self.rect.bottom = position_y
        self.vel = pygame.Vector2(0, 0)
        self.speed = 8192
        self.hp = 2048

    def update(self, delta_time, layout, player):
        """Scarecrow update function."""
        self.rect.x += self.vel.x * delta_time
        self._collisions(layout, 'x')
        self.rect.y += self.vel.y * delta_time
        self._collisions(layout, 'y')

    def _collisions(self, layout, direction):
        for y, row in enumerate(layout):
            for x, tile in enumerate(row):
                if tile == '#':
                    tile_rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    if self.rect.colliderect(tile_rect):
                        self._handle_collision(tile_rect, direction)

    def _handle_collision(self, tile_rect, direction):
        if direction == 'x':
            if self.rect.right - tile_rect.left < TILE_SIZE // 2:
                self.rect.right = tile_rect.left
                self.vel.x = 0
            elif self.rect.left - tile_rect.right > -TILE_SIZE // 2:
                self.rect.left = tile_rect.right
                self.vel.x = 0
        elif direction == 'y':
            if self.rect.bottom - tile_rect.top < TILE_SIZE // 2:
                self.rect.bottom = tile_rect.top
                self.vel.y = 0
            elif self.rect.top - tile_rect.bottom > -TILE_SIZE // 2:
                self.rect.top = tile_rect.bottom
                self.vel.y = 0

    def draw(self, screen):
        """Scarecrow draw function."""
        screen.blit(self.image, self.rect)

def generate_map():
    """Map generation function"""
    size_5 = MAP_SIZE // 5
    size_1 = MAP_SIZE - 1
    avoid_chars = ['P', '1', '2', '3']

    def generate():
        layout = [['#' if i % 2 == 0 or j in {0, size_1} or i in {0, size_1} else ' '
                   for j in range(MAP_SIZE)] for i in range(MAP_SIZE)]
        for i in range(1, size_1):
            if i % 2 == 0:
                rand_range = random.randrange(1, size_5)
                for _ in range(rand_range):
                    clime = random.randrange(1, size_1)
                    if layout[i - 1][clime] == ' ':
                        layout[i][clime] = ' '
            else:
                ml, mr = sorted(random.randrange(size_5 * 2, size_5 * 3) for _ in range(2))
                rand_range_start = random.randrange(1, size_5)
                rand_range_end = random.randrange(size_5 * 4, MAP_SIZE)
                for j in list(range(rand_range_start)) + \
                        list(range(rand_range_end, size_1)) + \
                        list(range(ml, mr)):
                    if layout[i - 1][j] == '#':
                        layout[i][j] = '#'
        return layout

    def validate(layout):
        visited = set()
        start = next((i, j) for i in range(MAP_SIZE)
                    for j in range(MAP_SIZE) if layout[i][j] == ' ')

        stack = [start]
        while stack:
            i, j = stack.pop()
            if (i, j) not in visited:
                visited.add((i, j))
                for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    ni, nj = i + di, j + dj
                    if 0 <= ni < MAP_SIZE and 0 <= nj < MAP_SIZE and layout[ni][nj] == ' ':
                        stack.append((ni, nj))

        return all(layout[i][j] != ' ' or (i, j) in visited
                    for i in range(MAP_SIZE) for j in range(MAP_SIZE))

    layout = generate()
    while not validate(layout):
        layout = generate()

    player = next((i, j) for i in range(size_1, 0, -1)
                    for j in range(MAP_SIZE) if layout[i][j] == ' ' and layout[i][j + 1] == ' ')
    layout[player[0]][player[1]] = 'P'

    for _ in range(random.randrange(5, 8)):
        while True:
            i, j = random.randrange(1, MAP_SIZE - 2, 2), random.randrange(1, MAP_SIZE - 1, 2)
            if (layout[i][j] == ' ' and layout[i + 1][j] == '#' and
                layout[i][j - 1] not in avoid_chars and
                layout[i][j + 1] not in avoid_chars):
                layout[i][j] = random.choice(['1', '2', '3'])
                break

    return layout

def handle_events(player):
    """Events handling function."""
    keys = pygame.key.get_pressed()
    player.move(-1 if keys[pygame.K_a] and not keys[pygame.K_d] else
                 1 if keys[pygame.K_d] and not keys[pygame.K_a] else 0)

    if keys[pygame.K_ESCAPE]:
        return False

    for event in pygame.event.get():
        if (event.type == pygame.QUIT or
            (event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE)):
            return False
        if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
            player.jump()

    return True

def main_menu(screen):
    """Main menu function."""
    menu_font = pygame.font.Font(None, 128)
    play_text = menu_font.render('Play', True, WHITE)
    quit_text = menu_font.render('Quit', True, WHITE)
    play_rect = pygame.Rect(SCREEN_WIDTH // 2 - play_text.get_width() // 2,
    SCREEN_HEIGHT // 2 - play_text.get_height(), play_text.get_width(), play_text.get_height())
    quit_rect = pygame.Rect(SCREEN_WIDTH // 2 - quit_text.get_width() // 2,
    SCREEN_HEIGHT // 2 + quit_text.get_height(), quit_text.get_width(), quit_text.get_height())

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONUP:
                if play_rect.collidepoint(pygame.mouse.get_pos()):
                    return True
                if quit_rect.collidepoint(pygame.mouse.get_pos()):
                    return False

        screen.fill(BLACK)
        screen.blit(play_text, play_rect.topleft)
        screen.blit(quit_text, quit_rect.topleft)
        pygame.display.update()

def level(screen):
    """Level function."""
    clock = pygame.time.Clock()
    sprites = pygame.sprite.Group()
    layout = generate_map()
    tile_to_class = {'P': Player, '1': Kamikaze, '2': Slasher, '3': Lancer}
    player = create_entities(layout, sprites, tile_to_class)
    while handle_events(player):
        sprites.update(clock.get_time() / 1000, layout, player)
        camera_x, camera_y = update_camera(player, layout, screen)
        draw_tiles(layout, screen, camera_x, camera_y)
        update_positions(sprites, camera_x, camera_y, player)
        for sprite in sprites:
            if sprite.hp == 0:
                sprites.remove(sprite)
        sprites.draw(screen)
        reset_positions(sprites, camera_x, camera_y, player)
        pygame.display.update()
        clock.tick(60)

def create_entities(layout, sprites, tile_to_class):
    """Entity creation function."""
    for y, row in enumerate(layout):
        for x, tile in enumerate(row):
            if tile in tile_to_class:
                entity = tile_to_class[tile](x*TILE_SIZE + TILE_SIZE // 2,
                                            y*TILE_SIZE if tile == '1' else (y + 1)*TILE_SIZE)
                sprites.add(entity)
                if tile == 'P':
                    player = entity
    return player

def update_camera(player, layout, screen):
    """Camera update function."""
    camera_x = min(max(player.rect.centerx - screen.get_width() // 2, 0),
                    len(layout[0])*TILE_SIZE - screen.get_width())
    camera_y = min(max(player.rect.centery - screen.get_height() // 2, 0),
                    len(layout)*TILE_SIZE - screen.get_height())
    return camera_x, camera_y

def draw_tiles(layout, screen, camera_x, camera_y):
    """Tile draw function."""
    screen.fill(BLACK)
    for y, row in enumerate(layout):
        if y*TILE_SIZE - camera_y >= 0 or y*TILE_SIZE - camera_y <= SCREEN_WIDTH:
            for x, tile in enumerate(row):
                if (tile == '#' and (x*TILE_SIZE - camera_x >= 0 or
                    x*TILE_SIZE - camera_x <= SCREEN_HEIGHT)):
                    tile = pygame.Rect((x*TILE_SIZE - camera_x), (y*TILE_SIZE - camera_y),
                                        TILE_SIZE, TILE_SIZE)
                    pygame.draw.rect(screen, WHITE, tile)

def update_positions(sprites, camera_x, camera_y, player):
    """Update position function."""
    player.rect.centerx -= camera_x
    player.rect.centery -= camera_y
    for sprite in sprites:
        if sprite != player:
            sprite.rect.centerx -= camera_x
            sprite.rect.centery -= camera_y

def reset_positions(sprites, camera_x, camera_y, player):
    """Reset position function."""
    player.rect.centerx += camera_x
    player.rect.centery += camera_y
    for sprite in sprites:
        if sprite != player:
            sprite.rect.centerx += camera_x
            sprite.rect.centery += camera_y

def main():
    """Main function."""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Game')

    while main_menu(screen):
        level(screen)

    pygame.quit()

if __name__ == '__main__':
    main()
