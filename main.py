"""This module contains a simple game using pygame."""
import random
import math
from typing import List
import heapq
import pygame
from pygame import K_a, K_d, K_SPACE, K_ESCAPE, KEYUP, QUIT, MOUSEBUTTONDOWN

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
ATTACK = False

class Player(pygame.sprite.Sprite):
    """Player sprite class."""
    def __init__(self, position_x, position_y):
        super().__init__()
        self.image = self._create_surface((64, 128), GREEN)
        self.rect = self.image.get_rect(centerx=position_x, bottom=position_y)
        self.sword_image = self._create_surface((96, 96), BLUE)
        self.sword_rect = self.sword_image.get_rect(centerx=self.rect.centerx,
                                                    centery=self.rect.centery)
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

    def attack(self, enemies, iterable: bool):
        """Attack function."""
        global ATTACK
        if not ATTACK:
            ATTACK = True
        if iterable:
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

    @staticmethod
    def _create_surface(size, color):
        surface = pygame.Surface(size)
        surface.fill(color)
        return surface

    def enabled(self, player):
        """Enable movement function."""
        if TILE_SIZE >= (player.rect.centery - self.rect.centery) >= 0 and \
            -1.5*TILE_SIZE <= (player.rect.centerx - self.rect.centerx) <= 1.5*TILE_SIZE:
            self.enable = True

    @staticmethod
    def heuristic(a, b):
        """Heuristic function."""
        return abs(b[0] - a[0]) + abs(b[1] - a[1])

    def neighbors(self, layout, current):
        """Neighbors function."""
        x, y = current
        directions = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
        neighbors = [(nx, ny) for nx, ny in directions if 0 <= nx < len(layout) and \
                        0 <= ny < len(layout[0]) and layout[nx][ny] != '#']
        return neighbors

    def a_star_search(self, layout, start, goal):
        """A* function."""
        frontier = []
        heapq.heappush(frontier, (0, start))
        came_from = {start: None}
        cost_so_far = {start: 0}

        while frontier:
            _, current = heapq.heappop(frontier)

            if current == goal:
                break

            for i in self.neighbors(layout, current):
                new_cost = cost_so_far[current] + 1
                if i not in cost_so_far or new_cost < cost_so_far[i]:
                    cost_so_far[i] = new_cost
                    priority = new_cost + self.heuristic(goal, i)
                    heapq.heappush(frontier, (priority, i))
                    came_from[i] = current

        return came_from, cost_so_far

    def reconstruct_path(self, came_from, start, goal):
        """Reconstruct path function."""
        if goal not in came_from:
            return []
        current = goal
        path = []
        while current != start:
            path.append(current)
            current = came_from[current]
        path.append(start)
        path.reverse()
        return path

    def move(self, player, layout, delta_time):
        """Move towards the player."""
        if TILE_SIZE >= (player.rect.centery - self.rect.centery) >= 0 and \
            -0.5*TILE_SIZE <= (player.rect.centerx - self.rect.centerx) <= 0.5*TILE_SIZE:
            direction = pygame.Vector2((player.rect.centerx - self.rect.centerx) / SCREEN_WIDTH,
                                        (player.rect.centery - self.rect.centery) / SCREEN_HEIGHT)
            self.vel = direction * self.speed
            self.rect.x += self.vel.x * delta_time
            self._collisions(layout, 0)
            self.rect.y += self.vel.y * delta_time
            self._collisions(layout, 1)
        else:
            for y in range(len(layout)):
                for x in range(len(layout)):
                    tile_rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    if tile_rect.top <= player.rect.centerx <= tile_rect.bottom and \
                        tile_rect.left <= player.rect.centery <= tile_rect.right:
                        print('player: ' + str(x + 1) + ' ' + str(y + 1))
                    if tile_rect.top <= self.rect.centerx <= tile_rect.bottom and \
                        tile_rect.left <= self.rect.centery <= tile_rect.right:
                        print('kamikaze: ' + str(x + 1) + ' ' + str(y + 1))

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
        self.sword_rect = self.sword_image.get_rect(centerx=self.rect.centerx,
                                                    centery=self.rect.centery)
        self.enable = False
        self.hp = 256

    @staticmethod
    def _create_surface(size, color):
        surface = pygame.Surface(size)
        surface.fill(color)
        return surface

    def enabled(self, player):
        """Enable movement function."""
        if TILE_SIZE >= (player.rect.centery - self.rect.centery) >= 0 and \
            -1.5*TILE_SIZE <= (player.rect.centerx - self.rect.centerx) <= 1.5*TILE_SIZE:
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
        self.sword_rect = self.sword_image.get_rect(centerx=self.rect.centerx,
                                                    centery=self.rect.centery)
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
        pygame.draw.rect(screen, "red",
                        ((SCREEN_WIDTH // 2) - 512, 32, 1024, 64))
        pygame.draw.rect(screen, "green",
                        ((SCREEN_WIDTH // 2) - 512, 32, 1024*(self.hp / 2048), 64))

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

def score(screen: pygame.Surface, start_time: int, hp: int) -> None:
    """Score function."""
    font = pygame.font.Font(None, 128)
    time = (pygame.time.get_ticks() - start_time) / 1000
    minute = math.floor(time / 60)
    second = math.floor(time) % 60
    score_text = font.render('Time: ' + str(minute) + ':' + str(second), True, WHITE)
    codebreaker_text = font.render('Achivement: Codebreaker', True, WHITE)
    one_hit_text = font.render('Achivement: One Hit', True, WHITE)
    score_rect = pygame.Rect(SCREEN_WIDTH // 2 - score_text.get_width() // 2,
                                SCREEN_HEIGHT // 2 - score_text.get_height(),
                                score_text.get_width(), score_text.get_height())
    codebreaker_rect = pygame.Rect(SCREEN_WIDTH // 2 - codebreaker_text.get_width() // 2,
                                SCREEN_HEIGHT // 2 + codebreaker_text.get_height(),
                                codebreaker_text.get_width(), codebreaker_text.get_height())
    one_hit_rect = pygame.Rect(SCREEN_WIDTH // 2 - one_hit_text.get_width() // 2,
                                SCREEN_HEIGHT // 2 + 2 * one_hit_text.get_height(),
                                one_hit_text.get_width(), one_hit_text.get_height())

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
        if hp <= 128:
            screen.blit(one_hit_text, one_hit_rect)
        pygame.display.update()

def game_over(screen: pygame.Surface, level: bool) -> None:
    """Game over function."""
    font = pygame.font.Font(None, 128)
    over_text = font.render('Game Over', True, WHITE)
    over_rect = pygame.Rect(SCREEN_WIDTH // 2 - over_text.get_width() // 2,
    SCREEN_HEIGHT // 2 - over_text.get_height(), over_text.get_width(), over_text.get_height())
    pacifist_text = font.render('Achivement: Pacifist', True, WHITE)
    pacifist_rect = pygame.Rect(SCREEN_WIDTH // 2 - pacifist_text.get_width() // 2,
    SCREEN_HEIGHT // 2 + pacifist_text.get_height(),
    pacifist_text.get_width(), pacifist_text.get_height())

    while True:
        keys = pygame.key.get_pressed()
        if keys[K_ESCAPE]:
            return None
        for event in pygame.event.get():
            if event.type == QUIT:
                return None

        global ATTACK
        screen.fill(BLACK)
        screen.blit(over_text, over_rect)
        if ATTACK is False and level is True:
            screen.blit(pacifist_text, pacifist_rect)
        pygame.display.update()

def level(screen: pygame.Surface, scene_id: int) -> None:
    """Level function."""
    clock = pygame.time.Clock()
    pygame.time.set_timer(pygame.USEREVENT, 1000)
    layout = generate_map(MAP_SIZE)
    player = create_player(layout)
    enemies = create_enemy(layout, scene_id)

    while handle_events(True, player, enemies):
        camera_x, camera_y = update_camera(player, layout, screen)
        entity_update(clock.get_time() / 1000, layout, player, enemies)
        update_positions(enemies, camera_x, camera_y, player)

        for enemy in enemies:
            if enemy.hp <= 0:
                enemies.remove(enemy)

        if player.hp <= 0:
            game_over(screen, False)
            return 0

        draw(screen, layout, enemies, player, camera_x, camera_y, True)
        reset_positions(enemies, camera_x, camera_y, player)
        if next_level(layout, player, camera_x, camera_y):
            return (scene_id + 1)
        pygame.display.update()
        clock.tick(60)
    return scene_id

def boss(screen: pygame.Surface) -> int:
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

    while handle_events(False, player, enemy):
        entity_update(clock.get_time() / 1000, layout, player, enemy)

        if enemy.hp <= 0:
            del enemy
            return player.hp

        if player.hp <= 0:
            game_over(screen, True)
            return None

        draw(screen, layout, enemy, player, camera_x, camera_y, False)
        pygame.display.update()
        clock.tick(60)

def create_player(layout: List[List[str]]):
    """Player creation function."""
    for i in range(1, MAP_SIZE - 2):
        if layout[MAP_SIZE - 2][i] == ' ':
            return Player(i*TILE_SIZE + TILE_SIZE // 2, (MAP_SIZE - 1)*TILE_SIZE)
    return None

def create_enemy(layout: List[List[str]], scene_id: int):
    """Enemy creation function."""
    enemy = pygame.sprite.Group()
    size_1 = MAP_SIZE - 1

    for _ in range(random.randrange(9, 13)):
        while True:
            i, j = random.randrange(1, size_1), random.randrange(1, size_1, 2)
            if layout[i][j] == ' ' and (layout[i + 1][j] == '#' or layout[i - 1][j] == '#'):
                if scene_id == 1:
                    enemy.add(Kamikaze(j*TILE_SIZE + random.randint(16, TILE_SIZE - 16),
                                        i*TILE_SIZE))
                elif scene_id == 2:
                    enemy.add(Slasher(j*TILE_SIZE + random.randint(32, TILE_SIZE - 32),
                                        (i + 1)*TILE_SIZE))
                elif scene_id == 3:
                    enemy.add(random.choice([Kamikaze(j*TILE_SIZE + \
                                            random.randint(16, TILE_SIZE - 16), i*TILE_SIZE),
                                            Slasher(j*TILE_SIZE + \
                                            random.randint(32, TILE_SIZE - 32), (i + 1)*TILE_SIZE)]))
                break

    return enemy

def handle_events(iterable: bool, player, enemy) -> bool:
    """Events handling function."""
    keys = pygame.key.get_pressed()
    player.move(-1 if keys[K_a] and not keys[K_d] else
                 1 if keys[K_d] and not keys[K_a] else 0)

    for event in pygame.event.get():
        if (event.type == QUIT or
            (event.type == KEYUP and event.key == K_ESCAPE)):
            return False
        if event.type == pygame.USEREVENT:
            player.hp -= 16
        if event.type == KEYUP and event.key == K_SPACE:
            player.jump()
        elif event.type == MOUSEBUTTONDOWN:
            player.attack(enemy, iterable)

    return True

def entity_update(delta_time: float, layout: List[List[str]], player, enemy) -> None:
    """Update entity function."""
    player.update(delta_time, layout)
    enemy.update(delta_time, layout, player)

def update_camera(player, layout: List[List[str]], screen: pygame.Surface):
    """Camera update function."""
    camera_x = min(max(player.rect.centerx - screen.get_width() // 2, 0),
                    len(layout[0])*TILE_SIZE - screen.get_width())
    camera_y = min(max(player.rect.centery - screen.get_height() // 2, 0),
                    len(layout)*TILE_SIZE - screen.get_height())

    return camera_x, camera_y

def draw(screen: pygame.Surface, layout: List[List[str]], enemies,
            player, camera_x, camera_y, iterate: bool) -> None:
    """Draw function."""
    screen.fill(BLACK)
    for y, row in enumerate(layout):
        if y*TILE_SIZE - camera_y >= 0 or y*TILE_SIZE - camera_y <= SCREEN_WIDTH:
            for x, tile in enumerate(row):
                if (tile in ['#', 'E'] and (x*TILE_SIZE - camera_x >= 0 or \
                    x*TILE_SIZE - camera_x <= SCREEN_HEIGHT)):
                    tile_rect = pygame.Rect((x*TILE_SIZE - camera_x),
                                            (y*TILE_SIZE - camera_y), TILE_SIZE, TILE_SIZE)
                    pygame.draw.rect(screen, WHITE if tile == '#' else YELLOW, tile_rect)

    if iterate:
        for enemy in enemies:
            enemy.draw(screen)
    else:
        enemies.draw(screen)
    player.draw(screen)

def next_level(layout: List[List[str]], player, camera_x: int, camera_y: int) -> bool:
    """Check for level exit."""
    for y, row in enumerate(layout):
        for x, tile in enumerate(row):
            if tile == 'E':
                tile_rect = pygame.Rect((x*TILE_SIZE - camera_x),
                                        (y*TILE_SIZE) - camera_y, TILE_SIZE, TILE_SIZE)
                if player.rect.colliderect(tile_rect):
                    return True
    return False

def update_positions(enemies, camera_x: int, camera_y: int, player) -> None:
    """Update position function."""
    player.rect.centerx -= camera_x
    player.rect.centery -= camera_y
    player.sword_rect.centerx -= camera_x
    player.sword_rect.centery -= camera_y
    for enemy in enemies:
        enemy.rect.centerx -= camera_x
        enemy.rect.centery -= camera_y

def reset_positions(enemies, camera_x: int, camera_y: int, player) -> None:
    """Reset position function."""
    player.rect.centerx += camera_x
    player.rect.centery += camera_y
    player.sword_rect.centerx += camera_x
    player.sword_rect.centery += camera_y
    for enemy in enemies:
        enemy.rect.centerx += camera_x
        enemy.rect.centery += camera_y

def init_game() -> pygame.Surface:
    """Init pygame function."""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Game')
    return screen

def main(scene_id: int = 0) -> None:
    """Main function."""
    screen = init_game()

    while True:
        if scene_id == 0:
            start_time = pygame.time.get_ticks()
            if main_menu(screen):
                return None
            scene_id = 1
        elif scene_id != 4:
            scene_id = level(screen, scene_id)
        else:
            hp = boss(screen)
            score(screen, start_time, hp)
            scene_id = 0

if __name__ == '__main__':
    main()
    pygame.quit()
