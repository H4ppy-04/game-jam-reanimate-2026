import random

DIALOGUE = {
    "enemy_win": [
        "Die!",
        "You think you can play god?",
        "Looks like I rolled better than you",
        "I rolled the dice... and your fate followed",
        "The dice whispered your downfall to me",
        "Luck didn't just choose me... it abandoned you"
        "My roll was perfect. Your hope wasn't",
        "The dice gods opened the door... and I walked through",
        "Your chances? I watched them crumble with every roll",
        "The dead whisper your defeat",
        "Luck kneels to me",
        "Your fate cracks beneath my roll",
        "The underworld chose your loss",
        "Back to the sands with you, feline",
        "Your claws fail you",
        "My roll sealed your doom",
        "Your claws cannot scratch fate",
        "I roll in darkness. You fall into it",
        "Your fate is lighter than a feather",
    ],
    "enemy_lose": [
        "Nooooo",
        "Ughhhh",
        "The dice betrayed me... I'll remember this",
        "The odds mocked me today... they won't next time",
        "A critical fail... but even the shadows rise again",
        "Guess the dice finally chose your side",
        "My luck just rolled off the table",
        "You win... for now",
        "The underworld remembers this",
        "A cat outrolled a god... how amusing",
        "You win, little spirit... but the sands will shift",
        "A small victory for a small creature",
        "The underworld bows to your roll",
        "You scratch destiny... and it yields",
        "Your victory burns hotter than Ra",
        "Your lick strikes like a serpent",
        "I taste defeat... bitter as desert dust",
        "Your roll... it stings",
        "Your luck strikes like a serpent",
    ],
    "shop_keeper": [
        # TODO
    ],
}

def get_dialogue(event: str) -> str:
    lines = DIALOGUE.get(event)
    if not lines:
        return ""
    return random.choice(lines)