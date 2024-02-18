"""The main game loop."""
import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FRAME_RATE, PLAYER_SPEED, PLAYER_MAX_JUMP
from events import events
from scenes import main_menu, levels, scoreboard
from entities import Kamikaze, Slasher, Impaler, Boss

def main():
    """Main function of the game"""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Game")
    clock = pygame.time.Clock()

    while True:
        match main_menu(screen):
            case _ in range(5):
                levels(screen, _)
            case 5:
                scoreboard()
            case 6:
                break

    pygame.quit()
