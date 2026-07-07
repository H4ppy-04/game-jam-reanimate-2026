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
        "Your luck strikes like a serpent",
        "I taste defeat... bitter as desert dust",
        "Your roll... it stings",
        "Your luck strikes like a serpent",
    ],
    "shopkeeper_entry": [
        "Welcome to my shop.",
        "Please, browse my wares.",
        "I'll help give you an edge in battle!",
        "I hope you've got money!",
        "Look at what the ca-... Oh! You are a cat!",
        "I hope you aren't a cat burglar!",
        "I don't accept hairballs as payment.",
    ],
    "shopkeeper_odd_purchase": [
        "1, 3, 5. That's... odd.",
        "This die rolls with a twist!",
        "Roll responsibly!",
        "May the odds be in your favour.",
    ],
    "shopkeeper_even_purchase": [
        "2, 4, 6. A pattern!",
        "This die gives you an EVEN advantage.",
        "Even the playing field!",
        "May the odds even out!",
    ],
    "shopkeeper_lowroll_purchase": [
        "Give them a low-blow!",
        "1, 2 or 3, don't bet high!",
    ],
    "shopkeeper_highroll_purchase": [
        "4, 5 or 6, how interesting!",
        "Become a high roller!",
        "Bet your best!",
    ],
    "shopkeeper_no_money": [
        # TODO
    ]
}


def get_dialogue(event: str) -> str:
    lines = DIALOGUE.get(event)
    if not lines:
        return ""
    return random.choice(lines)
