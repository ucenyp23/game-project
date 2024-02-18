"""The main game loop."""
import pygame
from events import events
from scenes import main_menu, levels, scoreboard
from entities import Kamikaze, Slasher, Impaler, Boss

def main():
    """Main function of the game"""
    pygame.init()
    screen = pygame.display.set_mode((1920, 1080))
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
