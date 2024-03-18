"""This module contains a simple game using pygame."""
from typing import List
import random
import pygame
import heapq
import time

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
        self.image = self._create_surface((64, 128), GREEN)
        self.rect = self.image.get_rect(centerx=position_x, bottom=position_y)
        self.vel = pygame.Vector2(0, 0)
        self.jump_counter = 0
        self.speed = 1024
        self.gravity = 16
        self.hp = 512
        self.sword_image = self._create_surface((64, 32), BLUE)
        self.sword_rect = self.sword_image.get_rect(centerx=self.rect.centerx, centery=self.rect.centery)
        self.direction = 0
        self.angle = 0

    @staticmethod
    def _create_surface(size, color):
        surface = pygame.Surface(size)
        surface.fill(color)
        return surface

    def update(self, delta_time, layout):
        """Player update function."""
        self.rect.x += self.vel.x * delta_time
        if self.direction == 1:
            self.sword_rect.centerx = self.rect.right
        elif self.direction == -1:
            self.sword_rect.centerx = self.rect.left
        self._collisions(layout, 'x')
        self.rect.y += self.vel.y * delta_time
        self.sword_rect.centery = self.rect.centery
        self._collisions(layout, 'y')

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
        self.direction = direction

    def jump(self):
        """Player jump function."""
        if self.jump_counter < 2:
            self.vel.y = -self.speed
            self.jump_counter += 1

    def attack(self):
        pass

    def draw(self, screen):
        """Player draw function."""
        screen.blit(self.image, self.rect)
        screen.blit(self.sword_image, self.sword_rect)

class Kamikaze(pygame.sprite.Sprite):
    """Kamikaze sprite class."""
    def __init__(self, position_x, position_y):
        super().__init__()
        self.image = self._create_surface((32, 32), RED)
        self.rect = self.image.get_rect(centerx = position_x, bottom = position_y)
        self.vel = pygame.Vector2(0, 0)
        self.speed = 2048
        self.hp = 128
        self.enable = False
        self.visible = False

    @staticmethod
    def _create_surface(size, color):
        surface = pygame.Surface(size)
        surface.fill(color)
        return surface

    def enabled(self, player):
        if -TILE_SIZE < (player.rect.centery - self.rect.centery) < TILE_SIZE and -3*TILE_SIZE < (player.rect.centerx - self.rect.centerx) < 3*TILE_SIZE:
            self.enable = True

    def move(self, player, layout):
        """Move towards the player."""
        player_center_x = player.rect.centerx
        player_center_y = player.rect.centery
        self_center_x = self.rect.centerx
        self_center_y = self.rect.centery
        screen_width_half = SCREEN_WIDTH // 2
        screen_height_half = SCREEN_HEIGHT // 2

        distance_to_player = ((player_center_x - self_center_x)**2 + (player_center_y - self_center_y)**2)**0.5
        if distance_to_player <= 1000:
            direction = pygame.Vector2((player_center_x - self_center_x) / screen_width_half,
                                        (player_center_y - self_center_y) / screen_height_half)
            self.vel = direction * self.speed
        else:
            self.vel = pygame.Vector2(0, 0)


    def update(self, delta_time, layout, player):
        """Kamikaze update function."""
        if player.rect.colliderect(self.rect):
            player.hp -= self.hp
            self.hp = 0
        if self.enable == False:
            self.enabled(player)
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
        self.image = self._create_surface((64, 128), RED)
        self.rect = self.image.get_rect(centerx = position_x, bottom = position_y)
        self.sword_image = self._create_surface((64, 32), GREEN)
        self.sword_rect = self.sword_image.get_rect(centerx=self.rect.centerx, centery=self.rect.centery)
        self.enable = False
        self.hp = 256

    @staticmethod
    def _create_surface(size, color):
        surface = pygame.Surface(size)
        surface.fill(color)
        return surface

    def enabled(self, player):
        if -TILE_SIZE < (player.rect.centery - self.rect.centery) < TILE_SIZE and -3*TILE_SIZE < (player.rect.centerx - self.rect.centerx) < 3*TILE_SIZE:
            self.enable = True

    def move(self, player):
        """Move towards the player."""
        self.rect.centerx = player.rect.centerx
        self.rect.centery = player.rect.centery

    def update(self, delta_time, layout, player):
        """Slasher update function."""
        if self.enable == False:
            self.enabled(player)
        elif random.random() < 0.025:
            self.move(player)
        self.sword_rect.centerx = self.rect.centerx
        self.sword_rect.centery = self.rect.centery

    def draw(self, screen):
        """Slasher draw function."""
        screen.blit(self.image, self.rect)
        screen.blit(self.sword_image, self.sword_rect)

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

def generate_map(map_size: int) -> List[List[str]]:
    """Map generation function"""
    size_1 = map_size - 1
    entities = ['1', '2']

    def generate_layout(map_size: int, size_1: int) -> List[List[str]]:
        size_5 = map_size // 5
        layout = [['#' if i % 2 == 0 or j in {0, size_1} or i in {0, size_1} else ' '
                   for j in range(map_size)] for i in range(map_size)]

        for i in range(1, size_1):
            if i % 2 == 0:
                rand_range = random.randrange(1, size_5)
                for _ in range(rand_range):
                    clime = random.randrange(1, size_1)
                    if layout[i - 1][clime] == ' ':
                        layout[i][clime] = ' '
            else:
                ml, mr = sorted(random.randrange(size_5 * 2, size_5 * 3) for _ in range(2))
                for j in list(range(random.randrange(1, size_5))) + \
                        list(range(random.randrange(size_5 * 4, map_size), size_1)) + \
                        list(range(ml, mr)):
                    if layout[i - 1][j] == '#':
                        layout[i][j] = '#'

        return layout

    def validate_layout(layout: List[List[str]], map_size: int) -> bool:
        visited = set()
        start = next((i, j) for i in range(map_size)
                    for j in range(map_size) if layout[i][j] == ' ')

        stack = [start]
        while stack:
            i, j = stack.pop()
            if (i, j) not in visited:
                visited.add((i, j))
                for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    ni, nj = i + di, j + dj
                    if 0 <= ni < map_size and 0 <= nj < map_size and layout[ni][nj] == ' ':
                        stack.append((ni, nj))

        return all(layout[i][j] != ' ' or (i, j) in visited
                    for i in range(map_size) for j in range(map_size))

    layout = generate_layout(map_size, size_1)
    while not validate_layout(layout, map_size):
        layout = generate_layout(map_size, size_1)

    return layout

def main_menu(screen):
    """Main menu function."""
    font = pygame.font.Font(None, 128)
    play_text = font.render('Play', True, WHITE)
    quit_text = font.render('Quit', True, WHITE)
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
        screen.blit(play_text, play_rect)
        screen.blit(quit_text, quit_rect)
        pygame.display.update()

def game_over(screen):
    """Game over function."""
    font = pygame.font.Font(None, 128)
    over_text = font.render('Game Over', True, WHITE)
    over_rect = pygame.Rect(SCREEN_WIDTH // 2 - over_text.get_width() // 2,
    SCREEN_HEIGHT // 2 - over_text.get_height() // 2, over_text.get_width(), over_text.get_height())

    while True:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            return None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None

        screen.fill(BLACK)
        screen.blit(over_text, over_rect)
        pygame.display.update()

def level(screen):
    """Level function."""
    clock = pygame.time.Clock()
    layout = generate_map(MAP_SIZE)
    player = create_player(layout)
    enemies = create_enemies(layout)
    while handle_events(player):
        delta_time = clock.get_time() / 1000
        enemies.update(delta_time, layout, player)
        player.update(delta_time, layout)
        camera_x, camera_y = update_camera(player, layout, screen)
        draw_tiles(layout, screen, camera_x, camera_y)
        update_positions(enemies, camera_x, camera_y, player)
        enemies = pygame.sprite.Group(enemy for enemy in enemies if enemy.hp != 0)
        if player.hp == 0:
            game_over(screen)
            break
        for enemy in enemies:
            enemy.draw(screen)
        player.draw(screen)
        reset_positions(enemies, camera_x, camera_y, player)
        pygame.display.update()
        clock.tick(60)

def create_player(layout):
    """Function to create a player."""
    x = MAP_SIZE // 2
    for i in range(1, MAP_SIZE - 1):
        if layout[i][MAP_SIZE - 1] == ' ':
            x = i
            print(x)
            break

    return Player(x*TILE_SIZE + TILE_SIZE // 2, (MAP_SIZE - 1)*TILE_SIZE)

def create_enemies(layout):
    """Enemies creation function."""
    enemies = pygame.sprite.Group()

    for _ in range(random.randrange(9, 13)):
        while True:
            i, j = random.randrange(1, MAP_SIZE - 1), random.randrange(1, MAP_SIZE - 1, 2)
            if layout[i][j] == ' ' and layout[i + 1][j] == '#':
                entity = random.choice([Kamikaze(j*TILE_SIZE + TILE_SIZE // 2, i*TILE_SIZE),
                                        Slasher(j*TILE_SIZE + TILE_SIZE // 2, (i + 1)*TILE_SIZE)])
                enemies.add(entity)
                break

    return enemies

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
        elif event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
            player.jump()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            player.attack()

    return True

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

def update_positions(enemies, camera_x, camera_y, player):
    """Update position function."""
    player.rect.centerx -= camera_x
    player.rect.centery -= camera_y
    player.sword_rect.centerx -= camera_x
    player.sword_rect.centery -= camera_y
    for enemy in enemies:
        enemy.rect.centerx -= camera_x
        enemy.rect.centery -= camera_y

def reset_positions(enemies, camera_x, camera_y, player):
    """Reset position function."""
    player.rect.centerx += camera_x
    player.rect.centery += camera_y
    player.sword_rect.centerx += camera_x
    player.sword_rect.centery += camera_y
    for enemy in enemies:
        enemy.rect.centerx += camera_x
        enemy.rect.centery += camera_y

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
