"""The main game loop."""
import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FRAME_RATE, PLAYER_SPEED, PLAYER_MAX_JUMPS
from player import Player
from events import events
from enemies import Kamikaze, Slasher, Impaler, Boss
from scenes import MainMenu, Levels, Scoreboard

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
        clock.tick(FRAME_RATE)

    pygame.quit()
