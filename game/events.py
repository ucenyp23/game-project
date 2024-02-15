def events(player, running):
    """Handle events."""
    for event in pygame.event.get():
        match event.type:
            case pygame.QUIT:
                return False
            case pygame.KEYUP:
                match event.key:
                    case pygame.K_a | pygame.K_d:
                        player.move(0)
            case pygame.KEYDOWN:
                match event.key:
                    case pygame.K_SPACE:
                        player.jump()
                    case pygame.K_a:
                        player.move(-1)
                    case pygame.K_d:
                        player.move(1)