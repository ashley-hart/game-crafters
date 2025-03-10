import pygame
import pygame.freetype  # Import the freetype module.


THIS CODE IS NOT MINE... IT CAME FROM A STACK OVERFLOW POST... DELETE THIS AND RESTART WITH THE ASCII MAP TUTORIAL IN THE OTHER FILE.

pygame.init()
screen = pygame.display.set_mode((800, 600))
GAME_FONT = pygame.freetype.SysFont("arial", 24)
running =  True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0,0,0))
    # You can use `render` and then blit the text surface ...
    text_surface, rect = GAME_FONT.render("Hello World!", (255, 255, 255))
    screen.blit(text_surface, (40, 250))
    # or just `render_to` the target surface.
    GAME_FONT.render_to(screen, (40, 350), "Hello World!", (255, 255, 255))

    pygame.display.flip()

pygame.quit()