import enum

import pygame

pygame.init()


display = pygame.display.set_mode((1920, 1080))

font = pygame.font.Font("./assets/Fonts/Kenney Pixel Square.ttf", 50)



class Dice:
    def __init__(self) -> None:
        pass


class GameState(enum.Enum):
    MENU = 0,
    GAME = 1


game_state = GameState.MENU

play_text = font.render("PLAY GAME", True, (255, 255, 255))

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()


    if game_state == game_state.MENU:
        print("game state menu active")
        display.fill((25, 25, 25))
        display.blit(play_text, (1920 / 2 - play_text.width / 2, 1080 / 2 - play_text.height / 2))
    

    pygame.display.update()
