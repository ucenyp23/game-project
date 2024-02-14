"""The main game loop."""
import pygame
from config import x 
from player import x
from events import x
from enemies import x
from scenes import x

def main():
    """Main function of the game"""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Game")
    clock = pygame.time.Clock()

    sprites = pygame.sprite.Group()

    while True:
        events()
        sprites.update()
        sprites.draw()
        pygame.display.update()
        clock.tick(60)

    pygame.quit()
