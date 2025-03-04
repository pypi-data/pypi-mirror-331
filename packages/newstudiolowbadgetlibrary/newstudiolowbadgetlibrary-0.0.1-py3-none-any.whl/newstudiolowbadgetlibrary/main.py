import pygame


def run_pygame():
    pygame.init()
    screen = pygame.display.set_mode((400, 300))
    pygame.display.set_caption("Minimal Pygame Example")
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((30, 30, 30))  # Dark gray background
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

