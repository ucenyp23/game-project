"""This module contains a simple game using pygame."""
from pygame import K_a, K_d, K_SPACE, K_ESCAPE, KEYUP, QUIT, MOUSEBUTTONDOWN
from typing import List
import random
import math
import pygame

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
TILE_SIZE = 256
MAP_SIZE = 17
LEVEL = 0
ATTACK = False

class Player(pygame.sprite.Sprite):
    """Player sprite class."""
    def __init__(self, position_x, position_y):
        super().__init__()
        self.image = self._create_surface((64, 128), GREEN)
        self.rect = self.image.get_rect(centerx=position_x, bottom=position_y)
        self.sword_image = self._create_surface((96, 96), BLUE)
        self.sword_rect = self.sword_image.get_rect(centerx=self.rect.centerx, centery=self.rect.centery)
        self.vel = pygame.Vector2(0, 0)
        self.jump_counter = 0
        self.speed = 1024
        self.gravity = 16
        self.hp = 1024
        self.direction = 0

    @staticmethod
    def _create_surface(size, color):
        surface = pygame.Surface(size)
        surface.fill(color)
        return surface

    def update(self, delta_time, layout):
        """Player update function."""
        self.rect.x += self.vel.x * delta_time
        if self.direction == 1:
            self.sword_rect.left = self.rect.centerx
        elif self.direction == -1:
            self.sword_rect.right = self.rect.centerx
        self._collisions(layout, 0)
        self.rect.y += self.vel.y * delta_time
        self.sword_rect.centery = self.rect.centery
        self._collisions(layout, 1)

    def _collisions(self, layout, direction):
        for y, row in enumerate(layout):
            for x, tile in enumerate(row):
                if tile == '#':
                    tile_rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    if self.rect.colliderect(tile_rect):
                        self._handle_collision(tile_rect, direction)
        if direction == 1:
            self.vel.y += self.gravity

    def _handle_collision(self, tile_rect, direction):
        if direction == 0:
            if self.rect.right - tile_rect.left < TILE_SIZE // 2:
                self.rect.right = tile_rect.left
                self.vel.x = 0
            elif self.rect.left - tile_rect.right > -TILE_SIZE // 2:
                self.rect.left = tile_rect.right
                self.vel.x = 0
        elif direction == 1:
            if self.rect.bottom - tile_rect.top < TILE_SIZE // 2:
                self.rect.bottom = tile_rect.top
                self.vel.y = 0
                self.jump_counter = 0
            elif self.rect.top - tile_rect.bottom > -TILE_SIZE // 2:
                self.rect.top = tile_rect.bottom
                self.vel.y = 0

    def move(self, direction):
        """Player move function."""
        self.vel.x = direction * self.speed
        self.direction = direction

    def jump(self):
        """Player jump function."""
        if self.jump_counter < 2:
            self.vel.y = -self.speed
            self.jump_counter += 1

    def attack(self, enemies):
        """Attack function."""
        global LEVEL, ATTACK
        if not ATTACK:
            ATTACK = True
        if LEVEL < 3:
            for enemy in enemies:
                if self.sword_rect.colliderect(enemy.rect):
                    enemy.hp -= 128
                    if self.hp + 128 <= 1024:
                        self.hp += 128
                    else:
                        self.hp = 1024
        else:
            if self.sword_rect.colliderect(enemies.rect):
                enemies.hp -= 128
                if self.hp + 128 <= 1024:
                    self.hp += 128
                else:
                    self.hp = 1024

    def draw(self, screen):
        """Player draw function."""
        screen.blit(self.image, self.rect)
        screen.blit(self.sword_image, self.sword_rect)
        pygame.draw.rect(screen, "red", (32, SCREEN_HEIGHT - 64, 256, 32))
        pygame.draw.rect(screen, "green", (32, SCREEN_HEIGHT - 64, 256*(self.hp / 1024), 32))

class Kamikaze(pygame.sprite.Sprite):
    """Kamikaze sprite class."""
    def __init__(self, position_x, position_y):
        super().__init__()
        self.image = self._create_surface((32, 32), RED)
        self.rect = self.image.get_rect(centerx = position_x, top = position_y)
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

    def move(self, player, layout, delta_time):
        """Move towards the player."""
        player_center_x = player.rect.centerx
        player_center_y = player.rect.centery
        screen_width_half = SCREEN_WIDTH // 2
        screen_height_half = SCREEN_HEIGHT // 2

        distance_to_player = ((player_center_x - self.rect.centerx)**2 + (player_center_y - self.rect.centery)**2)**0.5
        if distance_to_player <= 1000:
            direction = pygame.Vector2((player_center_x - self.rect.centerx) / screen_width_half,
                                        (player_center_y - self.rect.centery) / screen_height_half)
            self.vel = direction * self.speed
            self.rect.x += self.vel.x * delta_time
            self._collisions(layout, 0)
            self.rect.y += self.vel.y * delta_time
            self._collisions(layout, 1)
        else:
            self.vel = pygame.Vector2(0, 0)


    def update(self, delta_time, layout, player):
        """Kamikaze update function."""
        if player.rect.colliderect(self.rect):
            player.hp -= self.hp
            self.hp = 0
        if self.enable is False:
            self.enabled(player)
        else:
            self.move(player, layout, delta_time)

    def _collisions(self, layout, direction):
        for y, row in enumerate(layout):
            for x, tile in enumerate(row):
                if tile == '#':
                    tile_rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    if self.rect.colliderect(tile_rect):
                        self._handle_collision(tile_rect, direction)

    def _handle_collision(self, tile_rect, direction):
        if direction == 0:
            if self.rect.right - tile_rect.left < TILE_SIZE // 2:
                self.rect.right = tile_rect.left
                self.vel.x = 0
            elif self.rect.left - tile_rect.right > -TILE_SIZE // 2:
                self.rect.left = tile_rect.right
                self.vel.x = 0
        elif direction == 1:
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
        self.sword_image = pygame.Surface((128, 64))
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
        if self.enable is False:
            self.enabled(player)
        elif random.random() < 0.025:
            self.move(player)
        if random.random() < 0.025:
            self.attack(player)
        self.sword_rect.centerx = self.rect.centerx
        self.sword_rect.centery = self.rect.centery

    def attack(self, player):
        """Attack function."""
        if self.rect.colliderect(player.rect):
            player.hp -= 128

    def draw(self, screen):
        """Slasher draw function."""
        screen.blit(self.image, self.rect)

class Scarecrow(pygame.sprite.Sprite):
    """Scarecrow sprite class."""
    def __init__(self, position_x, position_y):
        super().__init__()
        self.image = self._create_surface((96, 192), RED)
        self.rect = self.image.get_rect(centerx = position_x, bottom = position_y)
        self.sword_image = pygame.Surface((128, 128))
        self.sword_rect = self.sword_image.get_rect(centerx=self.rect.centerx, centery=self.rect.centery)
        self.hp = 2048

    @staticmethod
    def _create_surface(size, color):
        surface = pygame.Surface(size)
        surface.fill(color)
        return surface

    def move(self, player):
        """Move towards the player."""
        self.rect.centerx = player.rect.centerx
        self.rect.centery = player.rect.centery

    def update(self, delta_time, layout, player):
        """Slasher update function."""
        if random.random() < 0.025:
            self.move(player)
        if random.random() < 0.025:
            self.attack(player)
        self.sword_rect.centerx = self.rect.centerx
        self.sword_rect.centery = self.rect.centery

    def attack(self, player):
        """Attack function."""
        if self.rect.colliderect(player.rect):
            player.hp -= 128

    def draw(self, screen):
        """Slasher draw function."""
        screen.blit(self.image, self.rect)
        pygame.draw.rect(screen, "red", ((SCREEN_WIDTH // 2) - 512, 32, 1024, 64))
        pygame.draw.rect(screen, "green", ((SCREEN_WIDTH // 2) - 512, 32, 1024*(self.hp / 2048), 64))

def generate_map(map_size: int) -> List[List[str]]:
    """Map generation function"""
    size_1 = map_size - 1
    size_5 = map_size // 5

    def generate_layout() -> List[List[str]]:
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

    def validate_layout(layout: List[List[str]]) -> bool:
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

    layout = generate_layout()
    while not validate_layout(layout):
        layout = generate_layout()

    for i in range(1, size_1):
        if layout[1][i] == ' ':
            layout[1][i] = 'E'
            break

    return layout

def main_menu(screen: pygame.Surface) -> bool:
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
            if event.type == QUIT:
                return True
            if event.type == MOUSEBUTTONDOWN:
                if play_rect.collidepoint(pygame.mouse.get_pos()):
                    return False
                if quit_rect.collidepoint(pygame.mouse.get_pos()):
                    return True

        screen.fill(BLACK)
        screen.blit(play_text, play_rect)
        screen.blit(quit_text, quit_rect)
        pygame.display.update()

def score(screen: pygame.Surface, start_time: int, player: int):
    """Score function."""
    font = pygame.font.Font(None, 128)
    time = (pygame.time.get_ticks() - start_time) / 1000
    minute = math.floor(time / 60)
    second = math.floor(time) % 60
    score_text = font.render('Time: ' + str(minute) + ':' + str(second), True, WHITE)
    codebreaker_text = font.render('Achivement: Codebreaker', True, WHITE)
    one_hit_text = font.render('Achivement: One Hit', True, WHITE)
    score_rect = pygame.Rect(SCREEN_WIDTH // 2 - score_text.get_width() // 2,
    SCREEN_HEIGHT // 2 - score_text.get_height(), score_text.get_width(), score_text.get_height())
    codebreaker_rect = pygame.Rect(SCREEN_WIDTH // 2 - score_text.get_width() // 2,
    SCREEN_HEIGHT // 2 + score_text.get_height(), score_text.get_width(), score_text.get_height())
    one_hit_rect = pygame.Rect(SCREEN_WIDTH // 2 - score_text.get_width() // 2,
    SCREEN_HEIGHT // 2 + 2 * score_text.get_height(), score_text.get_width(), score_text.get_height())

    while True:
        keys = pygame.key.get_pressed()
        if keys[K_ESCAPE]:
            return None
        for event in pygame.event.get():
            if event.type == QUIT:
                return None

        screen.fill(BLACK)
        screen.blit(score_text, score_rect)
        if time <= 60:
            screen.blit(codebreaker_text, codebreaker_rect)
        if player <= 128:
            screen.blit(one_hit_text, one_hit_rect)
        pygame.display.update()

def game_over(screen: pygame.Surface):
    """Game over function."""
    font = pygame.font.Font(None, 128)
    over_text = font.render('Game Over', True, WHITE)
    over_rect = pygame.Rect(SCREEN_WIDTH // 2 - over_text.get_width(),
    SCREEN_HEIGHT // 2 - over_text.get_height() // 2, over_text.get_width(), over_text.get_height())
    pacifist_text = font.render('Achivement: Pacifist', True, WHITE)
    pacifist_rect = pygame.Rect(SCREEN_WIDTH // 2 + over_text.get_width(),
    SCREEN_HEIGHT // 2 - over_text.get_height() // 2, over_text.get_width(), over_text.get_height())

    while True:
        keys = pygame.key.get_pressed()
        if keys[K_ESCAPE]:
            break
        for event in pygame.event.get():
            if event.type == QUIT:
                return None

        global LEVEL, ATTACK
        screen.fill(BLACK)
        screen.blit(over_text, over_rect)
        if LEVEL == 3 and ATTACK is False:
            screen.blit(pacifist_text, pacifist_rect)
        pygame.display.update()

def level(screen: pygame.Surface):
    """Level function."""
    clock = pygame.time.Clock()
    pygame.time.set_timer(pygame.USEREVENT, 1000)
    layout = generate_map(MAP_SIZE)
    player = create_player(layout)
    enemies = create_enemy(layout)

    while handle_events(player, enemies):
        entity_update(clock.get_time() / 1000, layout, player, enemies)
        camera_x, camera_y = update_camera(player, layout, screen)
        update_positions(enemies, camera_x, camera_y, player)

        for enemy in enemies:
            if enemy.hp <= 0:
                enemies.remove(enemy)

        if player.hp <= 0:
            game_over(screen)
            global LEVEL
            LEVEL = 0
            break

        draw(screen, layout, enemies, player, camera_x, camera_y)
        reset_positions(enemies, camera_x, camera_y, player)
        if next_level(layout, player, camera_x, camera_y):
            break
        pygame.display.update()
        clock.tick(60)

def boss(screen: pygame.Surface):
    """Boss Level function."""
    clock = pygame.time.Clock()
    layout = [['#', '#', '#', '#', '#', '#', '#', '#'],
                ['#', ' ', ' ', ' ', ' ', ' ', ' ', '#'],
                ['#', ' ', ' ', ' ', ' ', ' ', ' ', '#'],
                ['#', ' ', ' ', ' ', ' ', ' ', ' ', '#'],
                ['#', '#', '#', '#', '#', '#', '#', '#']]
    player = Player(TILE_SIZE + TILE_SIZE // 2, 4*TILE_SIZE)
    enemy = Scarecrow(6*TILE_SIZE + TILE_SIZE // 2, 4*TILE_SIZE)
    camera_x, camera_y = 0, 40

    while handle_events(player, enemy):
        entity_update(clock.get_time() / 1000, layout, player, enemy)

        if enemy.hp <= 0:
            del enemy
            break

        if player.hp <= 0:
            game_over(screen)
            break

        draw(screen, layout, enemy, player, camera_x, camera_y)
        pygame.display.update()
        clock.tick(60)
    
    return player.hp

def create_player(layout: List[List[str]]):
    """Player creation function."""
    for i in range(1, MAP_SIZE - 2):
        if layout[MAP_SIZE - 2][i] == ' ':
            return Player(i*TILE_SIZE + TILE_SIZE // 2, (MAP_SIZE - 1)*TILE_SIZE)

def create_enemy(layout: List[List[str]]):
    """Enemy creation function."""
    enemy = pygame.sprite.Group()
    tile_2 = TILE_SIZE // 2
    size_1 = MAP_SIZE - 1

    for _ in range(random.randrange(9, 13)):
        while True:
            i, j = random.randrange(1, size_1), random.randrange(1, size_1, 2)
            if layout[i][j] == ' ' and (layout[i + 1][j] == '#' or layout[i - 1][j] == '#'):
                if LEVEL == 0:
                    enemy.add(Kamikaze(j*TILE_SIZE + tile_2, i*TILE_SIZE))
                elif LEVEL == 1:
                    enemy.add(Slasher(j*TILE_SIZE + tile_2, (i + 1)*TILE_SIZE))
                elif LEVEL == 2:
                    enemy.add(random.choice([Kamikaze(j*TILE_SIZE + tile_2, i*TILE_SIZE),
                                            Slasher(j*TILE_SIZE + tile_2, (i + 1)*TILE_SIZE)]))
                break

    return enemy

def handle_events(player, enemy) -> bool:
    """Events handling function."""
    keys = pygame.key.get_pressed()
    player.move(-1 if keys[K_a] and not keys[K_d] else
                 1 if keys[K_d] and not keys[K_a] else 0)

    for event in pygame.event.get():
        if (event.type == QUIT or
            (event.type == KEYUP and event.key == K_ESCAPE)):
            global LEVEL
            LEVEL = 0
            return False
        if event.type == pygame.USEREVENT:
            player.hp -= 16
        if event.type == KEYUP and event.key == K_SPACE:
            player.jump()
        elif event.type == MOUSEBUTTONDOWN:
            player.attack(enemy)

    return True

def entity_update(delta_time, layout: List[List[str]], player, enemy):
    player.update(delta_time, layout)
    enemy.update(delta_time, layout, player)

def update_camera(player, layout: List[List[str]], screen: pygame.Surface):
    """Camera update function."""
    camera_x = min(max(player.rect.centerx - screen.get_width() // 2, 0),
                    len(layout[0])*TILE_SIZE - screen.get_width())
    camera_y = min(max(player.rect.centery - screen.get_height() // 2, 0),
                    len(layout)*TILE_SIZE - screen.get_height())

    return camera_x, camera_y

def draw(screen: pygame.Surface, layout: List[List[str]], enemies, player, camera_x, camera_y):
    """Draw function."""
    screen.fill(BLACK)
    for y, row in enumerate(layout):
        if y*TILE_SIZE - camera_y >= 0 or y*TILE_SIZE - camera_y <= SCREEN_WIDTH:
            for x, tile in enumerate(row):
                if (tile in ['#', 'E'] and (x*TILE_SIZE - camera_x >= 0 or x*TILE_SIZE - camera_x <= SCREEN_HEIGHT)):
                    tile_rect = pygame.Rect((x*TILE_SIZE - camera_x), (y*TILE_SIZE - camera_y), TILE_SIZE, TILE_SIZE)
                    pygame.draw.rect(screen, WHITE if tile == '#' else YELLOW, tile_rect)

    global LEVEL
    if LEVEL < 3:
        for enemy in enemies:
            enemy.draw(screen)
    else:
        enemies.draw(screen)
    player.draw(screen)

def next_level(layout: List[List[str]], player, camera_x, camera_y) -> bool:
    """Check for level exit."""
    global LEVEL
    for y, row in enumerate(layout):
        for x, tile in enumerate(row):
            if tile == 'E':
                tile_rect = pygame.Rect((x*TILE_SIZE - camera_x), (y*TILE_SIZE) - camera_y, TILE_SIZE, TILE_SIZE)
                if player.rect.colliderect(tile_rect):
                    LEVEL += 1
                    return True
    return False

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
    global LEVEL
    screen = init_game()

    while True:
        if LEVEL == 0:
            start_time = pygame.time.get_ticks()
            if main_menu(screen):
                break
        if LEVEL < 3:
            level(screen)
        elif LEVEL == 3:
            player = boss(screen)
            score(screen, start_time, player)
            LEVEL = 0

    pygame.quit()

def init_game()
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Game')
    return screen

if __name__ == '__main__':
    main()
