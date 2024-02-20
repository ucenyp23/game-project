def levels(screen, level_number):
    dt = 0
    while True:
        match events():
            case False:
                break
        sprites.update(dt)
        sprites.draw(screen)
        pygame.display.update()
        dt = clock.tick(60) / 1000
