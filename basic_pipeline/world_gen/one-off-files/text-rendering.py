import pygame
import pygame.freetype  # Import the freetype module.


pygame.init()
screen = pygame.display.set_mode((800, 600))
GAME_FONT = pygame.freetype.SysFont("times new roman", 24)
running =  True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0,0,0))
    # You can use `render` and then blit the text surface ...
    text_surface, rect = GAME_FONT.render("Hello World!", (255, 255, 255))
    screen.blit(text_surface, (350, 180))
    # or just `render_to` the target surface.
    GAME_FONT.render_to(screen, (350, 280), "Hello World!", (255, 255, 255))

    pygame.display.flip()

pygame.quit()