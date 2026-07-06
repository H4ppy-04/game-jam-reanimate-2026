import pygame

pygame.init()


display = pygame.display.set_mode((1920, 1080))

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()


    display.fill((0,0,0))
    pygame.display.update()
