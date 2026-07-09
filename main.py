import enum
import random
import socket
import sys
from pathlib import Path

import pygame
from loguru import logger

from dialogue import get_dialogue

pygame.init()

clock = pygame.time.Clock()

screen_info = pygame.display.Info()

MAX_TIMER_LIMIT = 50


def resource_path(relative_path: str) -> Path:
    base_path = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base_path / relative_path


sound_enabled = False
try:
    pygame.mixer.init()
    sound_enabled = True
except pygame.error as e:
    logger.warning(f"Sound disabed: {e}")


def queue_sound(sound: pygame.Sound, channel: pygame.mixer.Channel):
    if sound_enabled:
        channel.queue(sound)
    else:
        logger.warning(f"Failed to load sound: {sound}")


def play_sound(sound, channel: pygame.mixer.Channel, volume: float = 1.0, loops=-1):
    if sound_enabled:
        channel.set_volume(volume)
        channel.play(sound, loops)
        channel.set_volume(1.0)
    else:
        logger.warning(f"Failed to play sound")


def stop_sound(channel: pygame.mixer.Channel):
    if sound_enabled:
        channel.stop()
    else:
        logger.warning(f"Failed to stop sound")


def wrap_text(text: str, text_font: pygame.font.Font, max_width: int) -> list[str]:
    if not text or not text.strip():
        return []

    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = f"{current_line} {word}".strip()

        if not current_line:
            current_line = word
        elif text_font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines


def render_wrapped_text(
    text: str,
    text_font: pygame.font.Font,
    color,
    max_width: int,
    line_spacing: int = 5
) -> pygame.Surface:
    lines = wrap_text(text, text_font, max_width)

    if not lines:
        return pygame.Surface((1, 1), pygame.SRCALPHA)

    line_surfaces = [text_font.render(line, True, color) for line in lines]

    width = max(surface.get_width() for surface in line_surfaces)
    total_height = sum(surface.get_height() for surface in line_surfaces) + line_spacing * (len(line_surfaces) - 1)

    wrapped_surface = pygame.Surface((max(1, width), max(1, total_height)), pygame.SRCALPHA)

    y = 0
    for surface in line_surfaces:
        wrapped_surface.blit(surface, (0, y))
        y += surface.get_height() + line_spacing

    return wrapped_surface

music_channel = pygame.mixer.Channel(0)
sfx_channel = pygame.mixer.Channel(1)

purchased_dice = []

display = pygame.display.set_mode((1920, 1080))

shop_background = pygame.transform.scale_by(
    pygame.image.load(resource_path("assets/shopkeeper.png")), 10
)
font = pygame.font.Font(resource_path("assets/Fonts/Kenney Pixel Square.ttf"), 50)
button_font = pygame.font.Font(
    resource_path("assets/Fonts/Kenney Pixel Square.ttf"), 34
)
shop_font = pygame.font.Font(resource_path("assets/Fonts/Kenney Pixel Square.ttf"), 24)

dialogue_font = pygame.font.Font(resource_path("assets/Fonts/Kenney Pixel Square.ttf"), 18)

# queue_sound(resource_path("assets/mainMenu.wav"))
pygame.display.set_caption("Roll the Bones... | Main Menu")

green_health_sprite = pygame.transform.scale2x(
    pygame.image.load(resource_path("assets/lifeCellOn.png"))
)
red_health_sprite = pygame.transform.scale2x(
    pygame.image.load(resource_path("assets/lifeCellOff.png"))
)

round_cell_off = pygame.transform.scale2x(
    pygame.image.load(resource_path("assets/roundCellOff.png"))
)
round_cell_on = pygame.transform.scale2x(
    pygame.image.load(resource_path("assets/roundCellOn.png"))
)

game_background = pygame.image.load(resource_path("assets/playingMat.png"))
tile_sprite = pygame.image.load(resource_path("assets/brickTexture.png"))
tile_sprite_long = pygame.Surface((1920, 200))
for i in range(0, 1920, tile_sprite.width):
    tile_sprite_long.blit(tile_sprite, (i, 0))

button_sprite_size = pygame.transform.scale2x(
    pygame.image.load(resource_path("assets/button.png")).convert_alpha()
).get_rect()
button_small_sprite_size = (
    pygame.image.load(resource_path("assets/button.png")).convert_alpha().get_rect()
)

health_sprite_width = 10
health_sprite_height = 30

round_sprite_width = 40
round_sprite_height = 60

cursor_sprite = pygame.transform.scale2x(
    pygame.image.load(
        resource_path("assets/kenney_cursor-pixel-pack/Tiles/tile_0168.png")
    ).convert_alpha()
)
coin_sprite = pygame.transform.scale2x(
    pygame.image.load(resource_path("assets/coin.png")).convert_alpha()
)

menu_title_image = pygame.image.load(resource_path("assets/title.png")).convert_alpha()
menu_title_image_rect = menu_title_image.get_rect()
menu_background = pygame.image.load(resource_path("assets/mainmenuBg.png"))
menu_background_rect = menu_background.get_rect()
# logger.debug(menu_background_rect.size)

speech_dialogue_box = pygame.image.load(resource_path("assets/speechBubble.png"))
speech_dialogue_box_reverse = pygame.transform.rotate(speech_dialogue_box, 180)
speech_dialogue_box_upside_down = pygame.transform.flip(speech_dialogue_box, False, True)


roll_sfx = [
    pygame.mixer.Sound(resource_path(f"assets/diceRoll{i}.wav")) for i in range(1, 3)
]
queue_sound(pygame.Sound(resource_path("assets/gambling.wav")), music_channel)
shop_sound = pygame.Sound(resource_path("assets/shopping.wav"))

transition_sound = pygame.mixer.Sound(resource_path("assets/transition.wav"))
buy_sound = pygame.mixer.Sound(resource_path("assets/buyItem.mp3"))


class Objective(enum.Enum):
    ROLL_LOWEST_NUM = "Roll the lowest number!"
    ROLL_HIGHEST_NUM = "Roll the highest number!"


def get_random_objective() -> Objective:
    objective = random.choice([Objective.ROLL_LOWEST_NUM, Objective.ROLL_HIGHEST_NUM])
    return objective


current_objective = get_random_objective()


def draw_objective(surface: pygame.Surface, objective: Objective):
    text = button_font.render(
        f"Objective: {objective.value}", True, (220, 220, 220), (20, 20, 20)
    )
    surface.blit(text, (1920 / 2 - text.width / 2, 10))

dice_image = {
    "red": {
        "1": pygame.image.load(
            resource_path("assets/kenney_boardgame-pack/PNG/Dice/dieRed_border1.png")
        ).convert_alpha(),
        "2": pygame.image.load(
            resource_path("assets/kenney_boardgame-pack/PNG/Dice/dieRed_border2.png")
        ).convert_alpha(),
        "3": pygame.image.load(
            resource_path("assets/kenney_boardgame-pack/PNG/Dice/dieRed_border3.png")
        ).convert_alpha(),
        "4": pygame.image.load(
            resource_path("assets/kenney_boardgame-pack/PNG/Dice/dieRed_border4.png")
        ).convert_alpha(),
        "5": pygame.image.load(
            resource_path("assets/kenney_boardgame-pack/PNG/Dice/dieRed_border5.png")
        ).convert_alpha(),
        "6": pygame.image.load(
            resource_path("assets/kenney_boardgame-pack/PNG/Dice/dieRed_border6.png")
        ).convert_alpha(),
    },
    "white": {
        "1": pygame.image.load(
            resource_path("assets/kenney_boardgame-pack/PNG/Dice/dieWhite_border1.png")
        ).convert_alpha(),
        "2": pygame.image.load(
            resource_path("assets/kenney_boardgame-pack/PNG/Dice/dieWhite_border2.png")
        ).convert_alpha(),
        "3": pygame.image.load(
            resource_path("assets/kenney_boardgame-pack/PNG/Dice/dieWhite_border3.png")
        ).convert_alpha(),
        "4": pygame.image.load(
            resource_path("assets/kenney_boardgame-pack/PNG/Dice/dieWhite_border4.png")
        ).convert_alpha(),
        "5": pygame.image.load(
            resource_path("assets/kenney_boardgame-pack/PNG/Dice/dieWhite_border5.png")
        ).convert_alpha(),
        "6": pygame.image.load(
            resource_path("assets/kenney_boardgame-pack/PNG/Dice/dieWhite_border6.png")
        ).convert_alpha(),
    },
}


enemy_rounds_won = 0
player_rounds_won = 0

def reset_game():
    global total_lives, coins, enemy_dice, player_dice, current_round, player_rounds_won, enemy_rounds_won
    total_lives = 3
    player_rounds_won = 0
    enemy_rounds_won = 0
    current_round = 0
    coins = 6
    enemy_dice.inventory.clear()
    player_dice.inventory.clear()

    player_dice.add_dice(
        Dice.add_random().value, Dice.add_random().color, DieCategory.FAIR
    )
    player_dice.add_dice(
        Dice.add_random().value, Dice.add_random().color, DieCategory.FAIR
    )

    enemy_dice.add_dice(
        Dice.add_random().value, Dice.add_random().color, DieCategory.FAIR
    )
    enemy_dice.add_dice(
        Dice.add_random().value, Dice.add_random().color, DieCategory.FAIR
    )


class StoreItem(pygame.sprite.Sprite):
    def __init__(
        self, image: pygame.Surface, caption: str, x: int, y: int, price: int, *groups
    ):
        super().__init__(*groups)

        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.price = price

        self.caption = caption
        self.caption_render = shop_font.render(
            self.caption + f" (${str(self.price)})", True, (255, 255, 255), (20, 20, 20)
        )

        self.hovering = False

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        if self.hovering:
            surface.blit(
                self.caption_render,
                (
                    self.rect.centerx - self.caption_render.width / 2,
                    self.rect.bottom + (self.caption_render.height / 2),
                ),
            )


store_items = pygame.sprite.Group()

store_items.add(
    StoreItem(
        dice_image["white"]["1"],
        "Odd Only",
        1920 * 4 // 7,
        1080 * 1 // 4 - 100,
        price=3,
    ),
    StoreItem(
        dice_image["red"]["2"],
        "Even Only",
        1920 * 4 // 7 + 100,
        1080 * 1 // 4 - 100,
        price=3,
    ),
    StoreItem(
        dice_image["red"]["1"],
        "Low Roll",
        1920 * 4 // 7 + 200,
        1080 * 1 // 4 - 100,
        price=2,
    ),
    StoreItem(
        dice_image["red"]["6"],
        "High Roll",
        1920 * 4 // 7 + 300,
        1080 * 1 // 4 - 100,
        price=4,
    ),
)


class ButtonSmall:
    def __init__(self, x, y, text) -> None:
        self.image = pygame.image.load(
            resource_path("assets/button.png")
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
            pygame.image.load(resource_path("assets/button.png")).convert_alpha()
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


class DieCategory(enum.Enum):
    FAIR = "Fair"
    EVEN_ONLY = "Even Only"
    ODD_ONLY = "Odd Only"
    HIGH_ROLL = "High Roll"
    LOW_ROLL = "Low Roll"


class Die:
    def __init__(self, color, value, category=DieCategory.FAIR, uses=None):
        self.color = color
        self.value = value

        self.image = pygame.Surface((68, 68), pygame.SRCALPHA)
        self.rect = self.image.get_rect()

        self.uses = uses

        self.category = category

        self.selected = False

        self.caption = str(category.value)
        self.caption_render = shop_font.render(
            self.caption, True, (255, 255, 255), (20, 20, 20)
        )
        self.hovering = False

        if isinstance(uses, int):
            self.uses_render = pygame.Surface((40, 40))
            pygame.draw.circle(
                self.uses_render,
                (255, 0, 255),
                (self.rect.width - 10, self.rect.height - 10),
                15,
            )
            self.uses_font = pygame.font.Font(
                resource_path("assets/Fonts/Kenney Pixel Square.ttf"), 22
            )

    def render_surface(self):
        return dice_image[self.color][str(self.value)]

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        self.caption_render = shop_font.render(
            self.caption, True, (255, 255, 255), (20, 20, 20)
        )
        if isinstance(self.uses, int):
            surface.blit(
                self.uses_font.render(str(self.uses), True, (200, 0, 200)),
                (self.rect.bottomright),
            )
        if self.hovering:
            surface.blit(
                self.caption_render,
                (
                    self.rect.centerx - self.caption_render.width / 2,
                    self.rect.top - (self.caption_render.height),
                ),
            )
    


class Dice:

    PLAYER_START_X = 450

    def __init__(self, enemy=False) -> None:

        # Player should start out with 2 dice
        self.inventory: list[Die] = []

        self.roll_history = []

        self.throw_timer = 0

        self.in_center = False

        if enemy:
            self.x = 1920 / 2 - 68
            self.y = 100

        else:
            self.x = Dice.PLAYER_START_X
            self.y = 1080 - 100

        self.orig_x = self.x
        self.orig_y = self.y

        self.enemy = enemy

    def position_die(self, throwing=False):
        hotbar_interval = 0
        thrown_interval = 0

        for die in self.inventory:
            if throwing and die.selected:
                die.rect.x = self.x + thrown_interval
                die.rect.y = 1080 - 300 if not self.enemy else 300
                thrown_interval += die.rect.width + 30
            else:
                die.rect.x = Dice.PLAYER_START_X + hotbar_interval
                die.rect.y = 1080 - 100 if not self.enemy else 100
                hotbar_interval += die.rect.width + 30

    @staticmethod
    def add_random() -> Die:
        return Die(random.choice(["red", "white"]), random.randint(1, 6))

    def draw(self, surface):
        for die in self.inventory:
            die.draw(surface)

    def reset_position(self):
        self.x = self.orig_x
        self.y = self.orig_y
        self.in_center = False

    def get_rect(self):
        return pygame.rect.Rect(self.x, self.y, len(self.inventory) * 68, 68)

    def update(self):
        self.position_die(self.in_center)
        if self.in_center:
            self.throw_timer += 1
            # logger.debug(self.throw_timer)
            if self.throw_timer > MAX_TIMER_LIMIT:
                self.reset_position()
                self.throw_timer = 0
                # de-select all the die
                for die in self.inventory:
                    if die.selected:
                        die.selected = False

    def add_dice(self, number: int, color: str, category: DieCategory, uses=None):
        self.inventory.append(Die(color, number, category, uses))
        self.position_die()
        for die in self.inventory:
            die.image = die.render_surface()

    def get_size(self):
        return [sum([die.rect.width for die in self.inventory]), 68]
    
    def get_selected_size(self):
        selected = [die for die in self.inventory if die.selected]
        return [sum(die.rect.width for die in selected), 68]

    def throw(self):
        """throw dice into screen"""
        self.in_center = True

        self.x = 1920 / 2 - self.get_selected_size()[0] / 2 - 68
        self.y = 1080 - 300

        if self.enemy:
            self.y = 300
        self.roll_history.append(self.total())

    def total(self) -> int:
        return sum([die.value for die in self.inventory if die.selected])
    
def roll_die(die: Die):
    match die.category:
        case DieCategory.FAIR:
            die.value = random.randint(1, 6)
        case DieCategory.EVEN_ONLY:
            die.value = random.choice([2, 4, 6])
        case DieCategory.ODD_ONLY:
            die.value = random.choice([1, 3, 5])
        case DieCategory.HIGH_ROLL:
            die.value = random.choice([5, 6])
        case DieCategory.LOW_ROLL:
            die.value = random.choice([1, 2])
    die.color = random.choice(["red", "white"])
    die.image = die.render_surface()

class GameState(enum.Enum):
    MENU = 0
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


def draw_dialogue_box(surface, x, y, reverse=False, flip=False):
    if flip:
        surface.blit(speech_dialogue_box_upside_down, (x, y))
    elif reverse:
        surface.blit(speech_dialogue_box_reverse, (x, y))
    else:
        surface.blit(speech_dialogue_box, (x, y))


game_state = GameState.MENU

current_round = 1

last_thrown_dice = []

def render_round_num_text(current_round: int) -> pygame.Surface:
    text = button_font.render(
        f"Round {current_round}/3", True, (10, 10, 10), (200, 200, 200)
    )
    return text


round_num_text = render_round_num_text(current_round)
play_text = font.render("PLAY GAME", True, (109, 88, 0))
shop_text = font.render("DICE SHOP", True, (255, 255, 255))
game_over_text = font.render("GAME OVER", True, (255, 255, 255))
game_win_text = font.render("YOU WON!", True, (255, 255, 255))
artifacts_text = button_font.render("Artifacts (powerups)", True, (255, 255, 255))
dice_text = button_font.render("Dice", True, (255, 255, 255))
mx, my = 0, 0

coins = 6

# disable default cursor
pygame.mouse.set_visible(False)

player_healthbar = Healthbar(10, 10)
shop_button = Button(30, 1080 - (button_sprite_size.height + 10), "Shop")
throw_button = Button(
    1920 - 400, 1080 - (button_sprite_size.height + 10), "Throw!"
)
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


def draw_round_number(surface: pygame.Surface, current_round: int):
    for index in range(3):
        x = 1920 - 60 - (index * 40)
        if index < current_round:
            surface.blit(round_cell_on, (x, 20))
        else:
            surface.blit(round_cell_off, (x, 20))


total_lives = 3

player_dice = Dice()
enemy_dice = Dice(enemy=True)
# instantiate all enemy dice with selected being true

player_render_roll_text = shop_font.render("I haven't rolled yet", True, (0, 0, 0))
enemy_render_roll_text = shop_font.render("I haven't rolled yet", True, (0, 0, 0))

player_reaction_text = dialogue_font.render("", True, (0, 0, 0))
enemy_reaction_text = dialogue_font.render("", True, (0, 0, 0))

shopkeeper_text = button_font.render("", True, (0, 0, 0))
main_menu_timer = 0
main_menu_timer_max = 3

round_result_text = None
round_result_timer = 0
ROUND_RESULT_DURATION = 120 # total number of frames the message is visible for
ROUND_RESULT_FADE_FRAMES = 30 # How many frames are used for fading

def render_round_result(text: str, color) -> pygame.surface:
    return font.render(text, True, color)

def render_roll_text(roll) -> pygame.Surface:
    return font.render(f"I rolled a {roll}!", True, (0, 0, 0))

def player_speak_text(text, text_font=dialogue_font) -> pygame.Surface:
    return text_font.render(text, True, (0, 0, 0))

def wrap_text(text: str, text_font: pygame.font.Font, max_width: int) -> list[str]:
    words = text.split(" ")
    lines = []
    current_line = ""

    for word in words:
        test_line = f"{current_line} {word}".strip()
        if text_font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines

def render_wrapped_text(
    text: str,
    text_font: pygame.font.Font,
    color,
    max_width: int,
    line_spacing: int = 5
) -> pygame.Surface:
    lines = wrap_text(text, text_font, max_width)

    if not lines:
        return pygame.Surface((1, 1), pygame.SRCALPHA)

    line_surfaces = [text_font.render(line, True, color) for line in lines]

    width = max(surface.get_width() for surface in line_surfaces)
    total_height = sum(surface.get_height() for surface in line_surfaces) + line_spacing * (len(line_surfaces) - 1)

    wrapped_surface = pygame.Surface((max(1, width), max(1, total_height)), pygame.SRCALPHA)

    y = 0
    for surface in line_surfaces:
        wrapped_surface.blit(surface, (0, y))
        y += surface.get_height() + line_spacing

    return wrapped_surface

player_dice.add_dice(Dice.add_random().value, Dice.add_random().color, DieCategory.FAIR)
player_dice.add_dice(Dice.add_random().value, Dice.add_random().color, DieCategory.FAIR)

enemy_dice.add_dice(Dice.add_random().value, Dice.add_random().color, DieCategory.FAIR)
enemy_dice.add_dice(Dice.add_random().value, Dice.add_random().color, DieCategory.FAIR)
for die in enemy_dice.inventory:
    die.selected = True

enemy_roll_timer = 0
start_enemy_timer = False


play_sound(pygame.Sound(resource_path("assets/mainMenu.wav")), music_channel)


def _exit():
    pygame.quit()
    sys.exit()
    

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            _exit()

        if event.type == pygame.MOUSEMOTION:
            # logger.debug((mx, my))
            mx, my = pygame.mouse.get_pos()
            match game_state:
                case game_state.SHOP:
                    for sprite in store_items:
                        sprite.hovering = sprite.rect.collidepoint(mx, my)
                case game_state.GAME:
                    for die in player_dice.inventory:
                        die.hovering = die.rect.collidepoint(mx, my)

        if event.type == pygame.KEYDOWN:
            match game_state:
                case game_state.MENU:
                    if event.key == pygame.K_RETURN:
                        pygame.display.set_caption("Roll the Bones...")
                        game_state = game_state.GAME
                        play_sound(transition_sound, sfx_channel, 0.5, 0)
                        stop_sound(music_channel)
                        play_sound(
                            pygame.Sound(resource_path("assets/gambling.wav")), music_channel,
                        )
                    elif event.key == pygame.K_ESCAPE:
                        _exit()
                case game_state.GAME_OVER | game_state.WIN:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        game_state = game_state.MENU
                        pygame.display.set_caption("Roll the Bones... | Main Menu")
                        play_sound(transition_sound, sfx_channel, 0.5, 0)

        if event.type == pygame.MOUSEBUTTONDOWN:
            match game_state:
                case game_state.MENU:
                    play_sound(transition_sound, sfx_channel, 0.5, 0)
                    game_state = game_state.GAME
                    pygame.display.set_caption("Roll the Bones...")
                    stop_sound(music_channel)
                    play_sound(
                        pygame.Sound(resource_path("assets/gambling.wav")),
                        music_channel,
                    )

                case game_state.SHOP:
                    if shop_goback_button.rect.collidepoint(mx, my):
                        game_state = game_state.GAME

                        stop_sound(music_channel)
                        play_sound(
                            pygame.Sound(resource_path("assets/gambling.wav")),
                            music_channel,
                        )
                        pygame.display.set_caption("Roll the Bones...")

                    for item in store_items:
                        # If player has no coins
                        if item.rect.collidepoint(mx, my) and coins < item.price: 
                            shopkeeper_text = render_wrapped_text(
                                get_dialogue("shopkeeper_no_money"), shop_font, (0, 0, 0), 400
                            )

                        if item.rect.collidepoint(mx, my) and coins >= item.price:
                            # logger.info(f"Bought store item for ${item.price}")
                            play_sound(buy_sound, sfx_channel, loops=0)

                            coins -= item.price

                            match item.caption:
                                case "Odd Only":
                                    number = random.choice([1, 3, 5])
                                    color = "red"
                                    player_dice.add_dice(
                                        number, color, DieCategory.ODD_ONLY, uses=3
                                    )
                                    shopkeeper_text = render_wrapped_text(
                                        get_dialogue("shopkeeper_odd_purchase"), shop_font, (0, 0, 0), 400
                                    )
                                case "Even Only":
                                    number = random.choice([2, 4, 6])
                                    color = "white"
                                    player_dice.add_dice(
                                        number, color, DieCategory.EVEN_ONLY, uses=3
                                    )
                                    shopkeeper_text = render_wrapped_text(
                                        get_dialogue("shopkeeper_even_purchase"), shop_font, (0, 0, 0), 400
                                    )
                                case "High Roll":
                                    number = random.choice([5, 6])
                                    color = "white"
                                    player_dice.add_dice(
                                        number, color, DieCategory.HIGH_ROLL, uses=3
                                    )
                                    shopkeeper_text = render_wrapped_text(
                                        get_dialogue("shopkeeper_highroll_purchase"), shop_font, (0, 0, 0), 400
                                    )
                                case "Low Roll":
                                    number = random.choice([1, 2])
                                    color = "red"
                                    player_dice.add_dice(
                                        number, color, DieCategory.LOW_ROLL, uses=3
                                    )
                                    shopkeeper_text = render_wrapped_text(
                                        get_dialogue("shopkeeper_lowroll_purchase"), shop_font, (0, 0, 0), 400
                                    )

                case game_state.GAME:
                    if shop_button.rect.collidepoint(mx, my):
                        game_state = game_state.SHOP
                        stop_sound(music_channel)
                        play_sound(shop_sound, music_channel)
                        shopkeeper_text = render_wrapped_text(
                            get_dialogue("shopkeeper_entry"), shop_font, (0, 0, 0), 400
                        )
                        pygame.display.set_caption("Roll the Bones... | Shop")
                    selected = [i for i in player_dice.inventory if i.selected]
                    for die in player_dice.inventory:
                        if die.rect.collidepoint(mx, my):
                            if die.selected:
                                die.selected = False
                            if len(selected) < 2:
                                if die.selected == False:
                                    die.selected = True
                    if throw_button.rect.collidepoint(mx, my):
                        # logger.debug("throwing die")
                        # only able to throw if dice is selected
                        if len(selected):
                            for die in selected:
                                roll_die(die)

                            last_thrown_dice = selected.copy()
                            
                            player_dice.throw()
                            # Play rolling sfx
                            play_sound(random.choice(roll_sfx), sfx_channel, loops=0)

                            player_render_roll_text = render_roll_text(
                                player_dice.total()
                            )
                            start_enemy_timer = True

                case game_state.GAME_OVER | game_state.WIN:
                    game_state = game_state.MENU
                    pygame.display.set_caption("Roll the Bones... | Menu")

    if game_state == game_state.MENU:
        if main_menu_timer < 4:
            main_menu_timer += 1
            display.blit(menu_background, (0, 0))
        elif main_menu_timer < 8:
            display.blit(menu_background, (0, -1080))
            main_menu_timer = 0

        display.blit(
            menu_title_image, (1920 / 2 - (menu_title_image.width / 2), 150)
        )

        display.blit(
            play_text,
            (
                1920 / 2 - play_text.width / 2,
                (1080 / 2 - play_text.height / 2) - 100,
            ),
        )

    if game_state == game_state.SHOP:
        # choose dice

        display.blit(shop_background, (0, 0))

        # draw dialogue box, right below the shopkeeper's mouth
        draw_dialogue_box(display, 1920 * 2 / 7 + 40, 1080 * 2 / 5 - 75, flip=True)
        display.blit(
            shopkeeper_text, (
                1920 * 2 / 7 + 60, 1080 * 2 / 5
            )
        )

        display.blit(cursor_sprite, (mx, my))
        display.blit(
            shop_text,
            (
                1920 * 3 / 4
                - shop_text.width / 4
                - 25,  # On right side, on top of the Purple cloth
                1080 / 10 - shop_text.height / 2,
            ),
        )

        # draw lives still
        draw_player_health(display, total_lives)

        # button to go back
        shop_goback_button.draw(display)

        # draw money
        display.blit(
            coin_sprite, (1920 - (coin_sprite.get_rect().width + 150), 30)
        )
        display.blit(
            shop_font.render(f"{coins} Coins", False, (255, 255, 255)),
            (1920 - 150, 35),
        )

        for item in store_items:
            item.draw(display)

    if game_state == game_state.GAME:
        # display.fill((50, 50, 50))
        display.blit(game_background, (0, 0))

        # draw Healthbar
        draw_player_health(display, total_lives)
        draw_round_number(display, current_round)

        display.blit(tile_sprite_long, (0, 1080 - 200))

        # draw PLAYER dialogue box
        draw_dialogue_box(display, 150, 1080 // 2)
        display.blit(player_render_roll_text, (175, 1080 // 2 + 20))
        display.blit(
            player_reaction_text, (175, 1080 // 2 + 20 + player_reaction_text.height + 5
                                )
        )

        # draw ENEMY dialogue box
        draw_dialogue_box(
            display, 1920 - 500, 1080 // 10, reverse=True
        )
        display.blit(
            enemy_render_roll_text, (1920 - 480, 1080 // 10 + 90)
        )
        display.blit(
            enemy_reaction_text, (1920 - 480, 1080 // 10 + 90 + enemy_render_roll_text.height
                                )
        )

        # draw current roll objective
        draw_objective(display, current_objective)

        # draw dice
        player_dice.draw(display)
        enemy_dice.draw(display)

        for die in player_dice.inventory:
            if die.selected:
                pygame.draw.circle(
                    display, pygame.Color("Blue"), die.rect.center, die.rect.width, 3
                )

        # pygame.draw.rect(display, (255, 0, 0), player_dice.get_rect())

        player_dice.update()
        enemy_dice.update()

        shop_button.draw(display)
        throw_button.draw(display)

        if round_result_timer > 0:
            round_result_timer -= 1

            if round_result_timer < ROUND_RESULT_FADE_FRAMES:
                alpha = int(255 * (round_result_timer / ROUND_RESULT_FADE_FRAMES))
            else:
                alpha = 255

            faded_surface = round_result_text.copy()
            faded_surface.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)

            display.blit(
                faded_surface,
                (
                    1920 / 2 - faded_surface.width / 2,
                    1080 * 7/8 - faded_surface.height / 2,
                ),
            )

        display.blit(
            round_num_text, (1920 / 2 - round_num_text.width / 2, 620)
        )

        if start_enemy_timer:
            enemy_roll_timer += 1
            if enemy_roll_timer > MAX_TIMER_LIMIT:
                enemy_dice.throw()
                start_enemy_timer = False
                enemy_roll_timer = 0

                enemy_dice.inventory.clear()
                enemy_dice.add_dice(
                    Dice.add_random().value, Dice.add_random().color, DieCategory.FAIR
                )
                enemy_dice.add_dice(
                    Dice.add_random().value, Dice.add_random().color, DieCategory.FAIR
                )
                for die in enemy_dice.inventory:
                    die.selected = True
                enemy_render_roll_text = render_roll_text(enemy_dice.total())

                match current_objective:
                    case Objective.ROLL_HIGHEST_NUM:
                        if current_round < 3:
                            current_round += 1
                            round_num_text = render_round_num_text(current_round)
                            if (
                                enemy_dice.total()
                                > player_dice.roll_history[
                                    len(player_dice.roll_history) - 1
                                ]
                                ):
                                enemy_rounds_won += 1
                            else:
                                player_rounds_won += 1
                        else:
                            current_round = 1
                            round_num_text = render_round_num_text(current_round)
                            current_objective = get_random_objective()
                            if player_rounds_won < enemy_rounds_won:
                                total_lives -= 1
                                enemy_reaction_text = render_wrapped_text(
                                    get_dialogue("enemy_win"), shop_font, (0, 0, 0), 400,
                                )
                                player_reaction_text = render_wrapped_text(
                                    get_dialogue("player_lose"), shop_font, (0, 0, 0), 400
                                )
                                round_result_text = render_round_result(get_dialogue("player_loss_announcement"), (179, 38, 36))
                                round_result_timer = ROUND_RESULT_DURATION
                                # display.blit(player_speak_text("I lost... (ow)"), (175, 1080 // 2 + 20))
                                # display.blit(player_speak_text("I won!"), (1920 - 480, 1080 // 10 + 20))
                                if total_lives == 0:
                                    game_state = GameState.GAME_OVER
                                    pygame.display.set_caption(
                                        "Roll the Bones... | Game Over"
                                    )
                            else:
                                # the player won
                                coins += 3
                                total_lives += 1
                                enemy_reaction_text = render_wrapped_text(
                                    get_dialogue("enemy_lose"), shop_font, (0, 0, 0), 400
                                )
                                player_reaction_text = render_wrapped_text(
                                    get_dialogue("player_win"), shop_font, (0, 0, 0), 400
                                )
                                round_result_text = render_round_result(get_dialogue("player_win_announcement"), (35, 101, 51))
                                round_result_timer = ROUND_RESULT_DURATION
                                if total_lives > 9:
                                    game_state = GameState.WIN
                                    pygame.display.set_caption(
                                        "Roll the Bones... | You Won!"
                                    )
                                # display.blit(player_speak_text("I won!"), (175, 1080 // 2 + 20))
                                # display.blit(player_speak_text("I lost!?"), (1920 - 480, 1080 // 10 + 20))
                            player_rounds_won = 0
                            enemy_rounds_won = 0
                    case Objective.ROLL_LOWEST_NUM:
                        if current_round < 3:
                            current_round += 1
                            round_num_text = render_round_num_text(current_round)
                            if (
                                enemy_dice.total()
                                < player_dice.roll_history[
                                    len(player_dice.roll_history) - 1
                                ]
                                ):
                                enemy_rounds_won += 1
                            else:
                                player_rounds_won += 1

                        else:
                            current_round = 1

                            round_num_text = render_round_num_text(current_round)
                            current_objective = get_random_objective()
                            if player_rounds_won < enemy_rounds_won:

                                total_lives -= 1
                                enemy_reaction_text = render_wrapped_text(
                                    get_dialogue("enemy_win"), shop_font, (0, 0, 0), 400
                                )
                                player_reaction_text = render_wrapped_text(
                                    get_dialogue("player_lose"), shop_font, (0, 0, 0), 400
                                )
                                round_result_text = render_round_result(get_dialogue("player_loss_announcement"), (179, 38, 36))
                                round_result_timer = ROUND_RESULT_DURATION
                                # display.blit(player_speak_text("I lost... (ow)"), (175, 1080 // 2 + 20))
                                # display.blit(player_speak_text("I won!"), (1920 - 480, 1080 // 10 + 20))
                                if total_lives == 0:
                                    game_state = GameState.GAME_OVER
                                    pygame.display.set_caption(
                                        "Roll the Bones... | Game Over"
                                    )
                            else:
                                coins += 3
                                total_lives += 1
                                enemy_reaction_text = render_wrapped_text(
                                    get_dialogue("enemy_lose"), shop_font, (0, 0, 0), 400
                                )
                                player_reaction_text = render_wrapped_text(
                                    get_dialogue("player_lose"), shop_font, (0, 0, 0), 400
                                )
                                round_result_text = render_round_result(get_dialogue("player_win_announcement"), (35, 101, 51))
                                round_result_timer = ROUND_RESULT_DURATION
                                if total_lives > 9:
                                    game_state = GameState.WIN
                                    pygame.display.set_caption(
                                        "Roll the Bones... | You Won!"
                                    )
                            player_rounds_won = 0
                            enemy_rounds_won = 0

                for die in last_thrown_dice:
                    if isinstance(die.uses, int):
                        if die.uses == 1:
                            player_dice.inventory.remove(die)
                        else:
                            die.uses -= 1

    if game_state == game_state.GAME_OVER:
        reset_game()
        display.fill((20, 20, 20))
        display.blit(
            game_over_text,
            (
                1920 / 2 - game_over_text.width / 2,
                1080 / 2 - game_over_text.height / 2,
            ),
        )

    if game_state == game_state.WIN:
        reset_game()
        display.fill((20, 255, 30))
        display.blit(
            game_win_text,
            (
                1920 / 2 - game_win_text.width / 2,
                1080 / 2 - game_win_text.height / 2,
            ),
        )

    display.blit(cursor_sprite, (mx, my))

    pygame.display.update()
    clock.tick(60)
