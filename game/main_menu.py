from events import events

def main_menu(screen):
    while True:
        match events():
            case False:
                break
        sprites.update()
        sprites.draw(screen)
        pygame.display.update()
