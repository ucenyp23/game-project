def scoreboard(screen):
    while True:
        match events():
            case False:
                break
        sprites.update()
        sprites.draw(screen)
        pygame.display.update()
