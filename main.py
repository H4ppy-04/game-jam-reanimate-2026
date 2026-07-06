import enum

import random
import pygame

pygame.init()


display = pygame.display.set_mode((1920, 1080))

font = pygame.font.Font("./assets/Fonts/Kenney Pixel Square.ttf", 50)
button_font = pygame.font.Font("./assets/Fonts/Kenney Pixel Square.ttf", 34)

green_health_sprite = pygame.transform.scale2x(pygame.image.load("./assets/lifeCellGreen.png"))
red_health_sprite = pygame.transform.scale2x(pygame.image.load("./assets/lifeCellRed.png"))

button_sprite_size = pygame.transform.scale2x(pygame.image.load("./assets/kenney_ui-pack/PNG/Blue/Default//button_rectangle_border.png").convert_alpha()).get_rect()

health_sprite_width = 10
health_sprite_height = 30

cursor_sprite = pygame.transform.scale2x(pygame.image.load("./assets/kenney_cursor-pixel-pack/Tiles/tile_0168.png").convert_alpha())

dice_image = {
        "red": {
            "1": pygame.image.load(f"./assets/kenney_boardgame-pack/PNG/Dice/dieRed_border1.png").convert_alpha(),
            "2": pygame.image.load(f"./assets/kenney_boardgame-pack/PNG/Dice/dieRed_border2.png").convert_alpha(),
            "3": pygame.image.load(f"./assets/kenney_boardgame-pack/PNG/Dice/dieRed_border3.png").convert_alpha(),
            "4": pygame.image.load(f"./assets/kenney_boardgame-pack/PNG/Dice/dieRed_border4.png").convert_alpha(),
            "5": pygame.image.load(f"./assets/kenney_boardgame-pack/PNG/Dice/dieRed_border5.png").convert_alpha(),
            "6": pygame.image.load(f"./assets/kenney_boardgame-pack/PNG/Dice/dieRed_border6.png").convert_alpha()
            },
        "white": {
            "1": pygame.image.load(f"./assets/kenney_boardgame-pack/PNG/Dice/dieWhite_border1.png").convert_alpha(),
            "2": pygame.image.load(f"./assets/kenney_boardgame-pack/PNG/Dice/dieWhite_border2.png").convert_alpha(),
            "3": pygame.image.load(f"./assets/kenney_boardgame-pack/PNG/Dice/dieWhite_border3.png").convert_alpha(),
            "4": pygame.image.load(f"./assets/kenney_boardgame-pack/PNG/Dice/dieWhite_border4.png").convert_alpha(),
            "5": pygame.image.load(f"./assets/kenney_boardgame-pack/PNG/Dice/dieWhite_border5.png").convert_alpha(),
            "6": pygame.image.load(f"./assets/kenney_boardgame-pack/PNG/Dice/dieWhite_border6.png").convert_alpha()
            }
        }



class Button:
    def __init__(self, x, y, text) -> None:
        self.image = pygame.transform.scale2x(pygame.image.load("./assets/kenney_ui-pack/PNG/Blue/Default//button_rectangle_border.png").convert_alpha())
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.text = button_font.render(text, False, (0, 0, 0))
        self.image.blit(self.text, (self.rect.width / 2 - self.text.width / 2, self.rect.height / 2 - self.text.height / 2))

    def draw(self, display: pygame.Surface):
        display.blit(self.image, self.rect)


class Dice:
    def __init__(self) -> None:
        self.image = pygame.Surface((156, 68), pygame.SRCALPHA)
        self.roll()
        self.rect = self.image.get_rect()
        self.rect.x = 1920 // 2 - self.rect.width / 2
        self.rect.y = 1080 - 100

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def roll(self):
        self.red_die = dice_image["red"][random.choice([ i for i in dice_image["red"]])]
        self.red_die.set_colorkey((0, 0, 0))
        self.white_die = dice_image["white"][random.choice([i for i in dice_image["red"]])]
        self.white_die.set_colorkey((0, 0, 0))

        self.image.blit(self.red_die, (0, 0))
        self.image.blit(self.white_die, (self.red_die.get_rect().width + 5, 0))



class GameState(enum.Enum):
    MENU = 0,
    GAME = 1
    GAME_OVER = 2
    SHOP = 3


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


def draw_dialogue_box(surface, x, y):
    pygame.draw.rect(surface, (255, 255, 255), pygame.rect.Rect(x, y, 450, 250), 0, 20)
    pygame.draw.rect(surface, (20, 20, 20), pygame.rect.Rect(x, y, 450, 250), 10, 20)


game_state = GameState.MENU

play_text = font.render("PLAY GAME", True, (255, 255, 255))
shop_text = font.render("PLAYER SHOP", True, (255, 255, 255))
mx, my = 0, 0

# disable default cursor
pygame.mouse.set_visible(False)

player_healthbar = Healthbar(10, 10)
end_turn_button = Button(1920 - (button_sprite_size.width + 30), 1080 - (button_sprite_size.height + 200), "End Turn")
shop_button = Button(30, 1080 - (button_sprite_size.height + 10), "Shop")

def draw_player_health(surface: pygame.Surface, total_lives):
    index = 0

    for i in range(0, (9 * (health_sprite_width * 2)), health_sprite_width * 2):
        if index > 9:
            return;
        print(index)
        if index >= total_lives:
            surface.blit(red_health_sprite, (i, 10))
        else:
            surface.blit(green_health_sprite, (i, 10))
        index += 1


def draw_enemy_health(surface):
    # just a health bar
    health_bar_size = 150
    pygame.draw.rect(surface, (200, 0, 0), pygame.rect.Rect(1920 - health_bar_size - 10, 10, health_bar_size, 25))

total_lives = 3

dice = Dice()

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

                case game_state.SHOP:
                    ...

                case game_state.GAME:
                    if shop_button.rect.collidepoint(mx, my):
                        game_state = game_state.SHOP

                case game_state.GAME_OVER:
                    ...

    if game_state == game_state.MENU:
        display.fill((25, 25, 25))

        display.blit(play_text, (1920 / 2 - play_text.width / 2, 1080 / 2 - play_text.height / 2))

    if game_state == game_state.SHOP:
        # buy power ups
        # choose dice
        display.fill((50, 50, 50))

        display.blit(cursor_sprite, (mx, my))
        display.blit(shop_text, (1920 / 2 - shop_text.width / 2, 1080 / 10 - shop_text.height / 2))


    if game_state == game_state.GAME:
        display.fill((50, 50, 50))

        # draw Healthbar
        draw_player_health(display, total_lives)
        draw_enemy_health(display)

        # draw bar to have UI stuff blow it
        pygame.draw.rect(display, (20, 20, 20), pygame.rect.Rect(0, 1080 - 150, 1920, 20))

        # draw PLAYER dialogue box
        draw_dialogue_box(display, 150, 1080 // 2)

        # draw ENEMY dialogue box
        draw_dialogue_box(display, 1920 - 500, 1080 // 10)

        # draw dice
        dice.draw(display)

        # draw end turn button
        end_turn_button.draw(display)
        shop_button.draw(display)

    if game_state == game_state.GAME_OVER:
        # TODO: do game over stuff
        pass

    # cursor should apply across all game states
    display.blit(cursor_sprite, (mx, my))

    pygame.display.update()
