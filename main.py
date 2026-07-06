import enum
import random
import sys

import pygame
from loguru import logger

pygame.init()


display = pygame.display.set_mode((1920, 1080))

font = pygame.font.Font("./assets/Fonts/Kenney Pixel Square.ttf", 50)
button_font = pygame.font.Font("./assets/Fonts/Kenney Pixel Square.ttf", 34)
shop_font = pygame.font.Font("./assets/Fonts/Kenney Pixel Square.ttf", 24)

pygame.mixer.music.load("./assets/mainMenu.wav")
pygame.display.set_caption("Roll the Bones...")

green_health_sprite = pygame.transform.scale2x(
    pygame.image.load("./assets/lifeCellGreen.png")
)
red_health_sprite = pygame.transform.scale2x(
    pygame.image.load("./assets/lifeCellRed.png")
)

button_sprite_size = pygame.transform.scale2x(
    pygame.image.load(
        "./assets/kenney_ui-pack/PNG/Blue/Default//button_rectangle_border.png"
    ).convert_alpha()
).get_rect()
button_small_sprite_size = (
    pygame.image.load(
        "./assets/kenney_ui-pack/PNG/Blue/Default//button_rectangle_border.png"
    )
    .convert_alpha()
    .get_rect()
)

health_sprite_width = 10
health_sprite_height = 30

cursor_sprite = pygame.transform.scale2x(
    pygame.image.load(
        "./assets/kenney_cursor-pixel-pack/Tiles/tile_0168.png"
    ).convert_alpha()
)
coin_sprite = pygame.transform.scale2x(
    pygame.image.load("./assets/coin.png").convert_alpha()
)


class Objective(enum.Enum):
    ROLL_LOWEST_NUM = "Roll the lowest number!"
    ROLL_HIGHEST_NUM = "Roll the highest number!"


def get_random_objective() -> Objective:
    objective = random.choice([Objective.ROLL_LOWEST_NUM, Objective.ROLL_HIGHEST_NUM])
    return objective


current_objective = get_random_objective()


def draw_objective(surface: pygame.Surface, objective: Objective):
    text = button_font.render(f"Objective: {objective.value}", True, (220, 220, 220))
    surface.blit(text, (1920 / 2 - text.width / 2, 10))


dice_image = {
    "red": {
        "1": pygame.image.load(
            f"./assets/kenney_boardgame-pack/PNG/Dice/dieRed_border1.png"
        ).convert_alpha(),
        "2": pygame.image.load(
            f"./assets/kenney_boardgame-pack/PNG/Dice/dieRed_border2.png"
        ).convert_alpha(),
        "3": pygame.image.load(
            f"./assets/kenney_boardgame-pack/PNG/Dice/dieRed_border3.png"
        ).convert_alpha(),
        "4": pygame.image.load(
            f"./assets/kenney_boardgame-pack/PNG/Dice/dieRed_border4.png"
        ).convert_alpha(),
        "5": pygame.image.load(
            f"./assets/kenney_boardgame-pack/PNG/Dice/dieRed_border5.png"
        ).convert_alpha(),
        "6": pygame.image.load(
            f"./assets/kenney_boardgame-pack/PNG/Dice/dieRed_border6.png"
        ).convert_alpha(),
    },
    "white": {
        "1": pygame.image.load(
            f"./assets/kenney_boardgame-pack/PNG/Dice/dieWhite_border1.png"
        ).convert_alpha(),
        "2": pygame.image.load(
            f"./assets/kenney_boardgame-pack/PNG/Dice/dieWhite_border2.png"
        ).convert_alpha(),
        "3": pygame.image.load(
            f"./assets/kenney_boardgame-pack/PNG/Dice/dieWhite_border3.png"
        ).convert_alpha(),
        "4": pygame.image.load(
            f"./assets/kenney_boardgame-pack/PNG/Dice/dieWhite_border4.png"
        ).convert_alpha(),
        "5": pygame.image.load(
            f"./assets/kenney_boardgame-pack/PNG/Dice/dieWhite_border5.png"
        ).convert_alpha(),
        "6": pygame.image.load(
            f"./assets/kenney_boardgame-pack/PNG/Dice/dieWhite_border6.png"
        ).convert_alpha(),
    },
}


class ButtonSmall:
    def __init__(self, x, y, text) -> None:
        self.image = pygame.image.load(
            "./assets/kenney_ui-pack/PNG/Blue/Default//button_rectangle_border.png"
        ).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.text = button_font.render(text, False, (0, 0, 0))
        self.image.blit(
            self.text,
            (
                self.rect.width / 2 - self.text.width / 2,
                self.rect.height / 2 - self.text.height / 2,
            ),
        )

    def draw(self, display: pygame.Surface):
        display.blit(self.image, self.rect)


class Button:
    def __init__(self, x, y, text) -> None:
        self.image = pygame.transform.scale2x(
            pygame.image.load(
                "./assets/kenney_ui-pack/PNG/Blue/Default//button_rectangle_border.png"
            ).convert_alpha()
        )
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.text = button_font.render(text, False, (0, 0, 0))
        self.image.blit(
            self.text,
            (
                self.rect.width / 2 - self.text.width / 2,
                self.rect.height / 2 - self.text.height / 2,
            ),
        )

    def draw(self, display: pygame.Surface):
        display.blit(self.image, self.rect)


class Dice:
    SIZE = 156, 68

    def __init__(self, x, y) -> None:
        self.image = pygame.Surface((Dice.SIZE[0], Dice.SIZE[1]), pygame.SRCALPHA)

        self.roll_history = []
        self.roll()

        self.rect = self.image.get_rect()
        # self.rect.x = 1920 // 2 - self.rect.width / 2
        # self.rect.y = 1080 - 100
        self.rect.x = x
        self.rect.y = y

        self.origin = x, y

        self.throw_timer = 0

    def reset_position(self):
        self.rect.x = self.origin[0]
        self.rect.y = self.origin[1]

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def update(self):
        if self.rect.y != self.origin[1]:
            self.throw_timer += 1
            if self.throw_timer > 250:
                self.rect.x = self.origin[0]
                self.rect.y = self.origin[1]
                self.throw_timer = 0

    def roll(self):
        self.index_red = random.choice([i for i in dice_image["red"]])
        self.index_white = random.choice([i for i in dice_image["white"]])

        self.red_die = dice_image["red"][self.index_red]
        self.red_die.set_colorkey((0, 0, 0))
        self.white_die = dice_image["white"][self.index_white]
        self.white_die.set_colorkey((0, 0, 0))

        self.image.blit(self.red_die, (0, 0))
        self.image.blit(self.white_die, (self.red_die.get_rect().width + 5, 0))

        self.roll_history.append(self.total())

    def throw(self, enemy=False):
        """throw dice into screen"""
        self.roll()
        self.rect.x = 1920 / 2 - self.rect.width / 2
        self.rect.y = 1080 - 300

        if enemy:
            self.rect.x = 1920 / 2 - self.rect.width / 2
            self.rect.y = 300

    def total(self) -> int:
        _total = int(self.index_red) + int(self.index_white)
        logger.debug(f"total dice value: {_total}")
        return _total


class GameState(enum.Enum):
    MENU = (0,)
    GAME = 1
    GAME_OVER = 2
    SHOP = 3
    WIN = 4


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
game_over_text = font.render("GAME OVER", True, (255, 255, 255))
game_win_text = font.render("YOU WON!", True, (255, 255, 255))
artifacts_text = button_font.render("Artifacts (powerups)", True, (255, 255, 255))
dice_text = button_font.render("Dice", True, (255, 255, 255))
mx, my = 0, 0

coins = 0

# disable default cursor
pygame.mouse.set_visible(False)

player_healthbar = Healthbar(10, 10)
end_turn_button = Button(
    1920 - (button_sprite_size.width + 30),
    1080 - (button_sprite_size.height + 200),
    "End Turn",
)
shop_button = Button(30, 1080 - (button_sprite_size.height + 10), "Shop")
shop_goback_button = ButtonSmall(
    1920 - 200, 1080 / 2 - button_small_sprite_size.height, "Back"
)


def draw_player_health(surface: pygame.Surface, total_lives):
    index = 0

    for i in range(0, (9 * (health_sprite_width * 2)), health_sprite_width * 2):
        if index > 9:
            return
        if index >= total_lives:
            surface.blit(red_health_sprite, (i, 10))
        else:
            surface.blit(green_health_sprite, (i, 10))
        index += 1


def draw_enemy_health(surface):
    # just a health bar
    health_bar_size = 150
    pygame.draw.rect(
        surface,
        (200, 0, 0),
        pygame.rect.Rect(1920 - health_bar_size - 10, 10, health_bar_size, 25),
    )


total_lives = 3

player_dice = Dice(1920 // 2 - Dice.SIZE[0] / 2, 1080 - 100)
enemy_dice = Dice(1920 // 2 - Dice.SIZE[0] / 2, 100)

# begin playing menu music before anything
pygame.mixer.music.play(-1)

player_render_roll_text = shop_font.render("I haven't rolled yet", True, (0, 0, 0))
enemy_render_roll_text = shop_font.render("I haven't rolled yet", True, (0, 0, 0))


def render_roll_text(roll) -> pygame.Surface:
    return font.render(f"I rolled a {roll}!", True, (0, 0, 0))


def player_speak_text(text) -> pygame.Surface:
    return font.render(text, True, (0, 0, 0))


enemy_roll_timer = 0
start_enemy_timer = False

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEMOTION:
            mx, my = pygame.mouse.get_pos()
        if event.type == pygame.KEYDOWN:
            match game_state:
                case game_state.MENU:
                    if event.key == pygame.K_RETURN:
                        game_state = game_state.GAME

        if event.type == pygame.MOUSEBUTTONDOWN:
            match game_state:
                case game_state.MENU:
                    game_state = game_state.GAME
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load("./assets/gambling.wav")
                    pygame.mixer.music.play()

                case game_state.SHOP:
                    if shop_goback_button.rect.collidepoint(mx, my):
                        game_state = game_state.GAME

                case game_state.GAME:
                    if shop_button.rect.collidepoint(mx, my):
                        game_state = game_state.SHOP

                    if player_dice.rect.collidepoint(mx, my):
                        player_dice.throw()
                        player_render_roll_text = render_roll_text(player_dice.total())
                        start_enemy_timer = True

                    pygame.mixer.music.stop()

                case game_state.GAME_OVER:
                    game_state = game_state.MENU

    if game_state == game_state.MENU:
        display.fill((25, 25, 25))

        display.blit(
            play_text, (1920 / 2 - play_text.width / 2, 1080 / 2 - play_text.height / 2)
        )

    if game_state == game_state.SHOP:
        # buy power ups
        # choose dice
        display.fill((50, 50, 50))

        display.blit(cursor_sprite, (mx, my))
        display.blit(
            shop_text,
            (1920 / 2 - shop_text.width / 2, 1080 / 10 - shop_text.height / 2),
        )

        # draw lives still
        draw_player_health(display, total_lives)

        # button to go back
        shop_goback_button.draw(display)

        # draw money
        display.blit(coin_sprite, (1920 - (coin_sprite.get_rect().width + 120), 15))
        display.blit(
            shop_font.render(f"{coins} Coins", False, (255, 255, 255)), (1920 - 120, 20)
        )

        # middle line through screen
        pygame.draw.rect(display, (10, 10, 10), pygame.rect.Rect(0, 1080 / 2, 1920, 25))

        # draw artifacts text
        display.blit(artifacts_text, (1920 / 7, (1080 / 2) + 20))

        # draw line from center, center, to center, bottom
        pygame.draw.rect(
            display, (10, 10, 10), pygame.rect.Rect(1920 / 2, 1080 / 2, 25, 1080 / 2)
        )

        display.blit(dice_text, (1920 - 500, 1080 / 2 + 20))

    if game_state == game_state.GAME:
        display.fill((50, 50, 50))

        # draw Healthbar
        draw_player_health(display, total_lives)
        draw_enemy_health(display)

        # draw bar to have UI stuff blow it
        pygame.draw.rect(
            display, (20, 20, 20), pygame.rect.Rect(0, 1080 - 150, 1920, 20)
        )

        # draw PLAYER dialogue box
        draw_dialogue_box(display, 150, 1080 // 2)
        display.blit(player_render_roll_text, (175, 1080 // 2 + 20))

        # draw ENEMY dialogue box
        draw_dialogue_box(display, 1920 - 500, 1080 // 10)
        display.blit(enemy_render_roll_text, (1920 - 480, 1080 // 10 + 20))

        # draw current roll objective
        draw_objective(display, current_objective)

        # draw dice
        player_dice.draw(display)
        enemy_dice.draw(display)

        player_dice.update()
        enemy_dice.update()

        # draw end turn button
        end_turn_button.draw(display)
        shop_button.draw(display)

        if start_enemy_timer:
            enemy_roll_timer += 1
            if enemy_roll_timer > 250:
                enemy_dice.roll()
                enemy_dice.throw(enemy=True)
                start_enemy_timer = False
                enemy_roll_timer = 0
                enemy_render_roll_text = render_roll_text(enemy_dice.total())
                match current_objective:
                    case Objective.ROLL_HIGHEST_NUM:
                        if (
                            enemy_dice.total()
                            > player_dice.roll_history[
                                len(player_dice.roll_history) - 1
                            ]
                        ):
                            total_lives -= 1
                            # display.blit(player_speak_text("I lost... (ow)"), (175, 1080 // 2 + 20))
                            # display.blit(player_speak_text("I won!"), (1920 - 480, 1080 // 10 + 20))
                            if total_lives == 0:
                                game_state = GameState.GAME_OVER
                        else:
                            # the player won
                            coins += 1
                            total_lives += 1
                            if total_lives > 9:
                                game_state = GameState.WIN
                            # display.blit(player_speak_text("I won!"), (175, 1080 // 2 + 20))
                            # display.blit(player_speak_text("I lost!?"), (1920 - 480, 1080 // 10 + 20))

                    case Objective.ROLL_LOWEST_NUM:
                        if (
                            enemy_dice.total()
                            < player_dice.roll_history[
                                len(player_dice.roll_history) - 1
                            ]
                        ):
                            total_lives -= 1
                            # display.blit(player_speak_text("I lost... (ow)"), (175, 1080 // 2 + 20))
                            # display.blit(player_speak_text("I won!"), (1920 - 480, 1080 // 10 + 20))
                            if total_lives == 0:
                                game_state = GameState.GAME_OVER
                        else:
                            coins += 1
                            total_lives += 1
                            if total_lives > 9:
                                GameState.WIN

    if game_state == game_state.GAME_OVER:
        # TODO: do game over stuff
        display.fill((20, 20, 20))
        display.blit(
            game_over_text,
            (1920 / 2 - game_over_text.width / 2, 1080 / 2 - game_over_text.height / 2),
        )

    if game_state == game_state.WIN:
        display.fill((20, 255, 30))
        display.blit(
            game_win_text,
            (1920 / 2 - game_win_text.width / 2, 1080 / 2 - game_win_text.height / 2),
        )

    # cursor should apply across all game states
    display.blit(cursor_sprite, (mx, my))

    pygame.display.update()
