import enum

import pygame

pygame.init()


display = pygame.display.set_mode((1920, 1080))

font = pygame.font.Font("./assets/Fonts/Kenney Pixel Square.ttf", 50)

# health_sprite = pygame.image.load()



class Dice:
    def __init__(self) -> None:
        pass


class GameState(enum.Enum):
    MENU = 0,
    GAME = 1
    GAME_OVER = 2


class Healthbar(pygame.sprite.Sprite):
    def __init__(self, x, y, *groups) -> None:
        super().__init__(*groups)

        width = 150
        height = 50
        self.image = pygame.Surface((width, height))
        self.image.fill((255, 0, 0))

        self.rect = pygame.rect.Rect(x, y, width, height)

    def draw(self, display):
        display.blit(self.image, self.rect)

game_state = GameState.MENU

play_text = font.render("PLAY GAME", True, (255, 255, 255))
mx, my = 0, 0

player_healthbar = Healthbar(10, 10)

def draw_player_health(surface):
    cell_width = 10
    spacing = 20 # pixels
    for i in range(0, (9 * cell_width) * 2, spacing):
        pygame.draw.rect(surface, (0, 200, 0), pygame.rect.Rect(i, 10, 10, 25))


def draw_enemy_health(surface):
    # just a health bar
    health_bar_size = 150
    pygame.draw.rect(surface, (200, 0, 0), pygame.rect.Rect(1920 - health_bar_size - 10, 10, health_bar_size, 25))

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()

        if event.type == pygame.MOUSEMOTION:
            mx, my = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN:
            match game_state:
                case game_state.MENU:
                    game_state = game_state.GAME


    if game_state == game_state.MENU:
        print("game state menu active")
        display.fill((25, 25, 25))
        display.blit(play_text, (1920 / 2 - play_text.width / 2, 1080 / 2 - play_text.height / 2))

    if game_state == game_state.GAME:
        print("actual game screen")
        display.fill((50, 50, 50))

        # draw Healthbar
        draw_player_health(display)
        draw_enemy_health(display)

        # draw bar to have UI stuff blow it
        pygame.draw.rect(display, (20, 20, 20), pygame.rect.Rect(0, 1080 - 150, 1920, 20))

    if game_state == game_state.GAME_OVER:
        # TODO: do game over stuff
        pass

    pygame.display.update()
