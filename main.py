from dataclasses import dataclass
from random import sample
from drafter import *
from bakery import assert_equal


@dataclass
class Challenge:
    hidden_message: str
    encoded_text: str
    difficulty: str
    completed: bool
    hint: str
    hint_used: bool


@dataclass
class State:
    username: str
    score: int
    challenges: list[Challenge]
    current_challenge: int
    status: str
    last_encoded: str


def puzzle_bank() -> list[Challenge]:
    # 15 handcrafted puzzles; the game selects 3 from each difficulty.
    return [
        Challenge("TIGER", "Travelers Investigate Golden Evening Rivers", "Easy", False,
                  "Read the first letter of every word.", False),
        Challenge("OCEAN", "pianO musiC treE pizzA suN", "Easy", False,
                  "Read the final letter of every word.", False),
        Challenge("MUSIC", "Morning arrives quietly.\nUnder the trees.\nSilver clouds drift.\nInside the garden.\nClouds gather slowly.", "Easy", False,
                  "Read the first letter of each line.", False),
        Challenge("DREAM", "Distant Rivers Echo Across Mountains", "Easy", False,
                  "Read the first letter of every word.", False),
        Challenge("LIGHT", "shelL kiwI rinG patH planT", "Easy", False,
                  "Read the final letter of every word.", False),

        Challenge("SHADOW", "quiet Stars old Hills tiny Apples distant Dreams silent Owls bright Waves", "Medium", False,
                  "Read the first letter of every second word.", False),
        Challenge("CIPHER", "soft Clouds green Islands quiet Pines warm Hills bright Echoes distant Rivers", "Medium", False,
                  "Read the first letter of every second word.", False),
        Challenge("SECRET", "Silent footsteps approach. Every window closes. Curious travelers listen. Rivers flow quietly. Evening comes early. Travelers return home.", "Medium", False,
                  "Read the first letter of each sentence.", False),
        Challenge("GALAXY", "The quiet Garden beneath tall Apples beside hidden Lakes where silver Animals hear distant Xylophones under golden Yews", "Medium", False,
                  "Read the first letter of every third word.", False),
        Challenge("SIGNAL", "The Sun sets.\nAn Indigo bird sings.\nA Golden light shines.\nThe Northern wind rises.\nAn Ancient tower stands.\nA Lonely traveler waits.", "Medium", False,
                  "Read the first letter of the second word on each line.", False),

        Challenge("PHANTOM", "Mysterious Owls Travel Near Ancient Hidden Paths", "Hard", False,
                  "Take the first letters of all words, then reverse their order.", False),
        Challenge("ENIGMA", "quiet Astronauts distant Mountains blue Gardens small Islands silver Nights calm Echoes", "Hard", False,
                  "Take the first letter of every second word, then reverse the result.", False),
        Challenge("ECLIPSE", "In the valley\nEvening arrives\nBehind the clouds\nSilent birds rest\nAlong the path\nPine trees sway\nUnder the sky\nIslands appear\nFar away\nLanterns glow\nAt sunrise\nClouds drift\nOn the hill\nEvening returns", "Hard", False,
                  "Read the first letters of the even-numbered lines, then reverse them.", False),
        Challenge("WHISPER", "Rivers rush past. Every traveler listens. Paths twist ahead. Silent forests wait. Inside, the lights glow. Hidden doors open. Wandering stars fade.", "Hard", False,
                  "Take the first letters of the sentences, then reverse their order.", False),
        Challenge("PARADOX", "At dawn Xylophones in town Open while birds Dance beside tall Apples past rushing Rivers among quiet Animals near old Pines", "Hard", False,
                  "Read the first letter of every third word, then reverse the result.", False)
    ]


def create_challenges() -> list[Challenge]:
    bank = puzzle_bank()
    chosen = []
    for difficulty in ["Easy", "Medium", "Hard"]:
        matching = []
        for challenge in bank:
            if challenge.difficulty == difficulty:
                matching.append(challenge)
        chosen.extend(sample(matching, 3))
    return chosen


def calculate_points(challenge: Challenge) -> int:
    if challenge.difficulty == "Easy":
        points = 10
    elif challenge.difficulty == "Medium":
        points = 20
    else:
        points = 30
    if challenge.hint_used:
        points = points // 2
    return points


def check_answer(answer: str, secret: str) -> bool:
    return answer.strip().upper() == secret.upper()


def count_completed(challenges: list[Challenge]) -> int:
    total = 0
    for challenge in challenges:
        if challenge.completed:
            total += 1
    return total


# Optional create-your-own-message tool using first-letter steganography.
WORD_BANK = {
    "A": "Ancient", "B": "Bright", "C": "Curious", "D": "Distant",
    "E": "Evening", "F": "Friendly", "G": "Golden", "H": "Hidden",
    "I": "Interesting", "J": "Joyful", "K": "Kind", "L": "Little",
    "M": "Misty", "N": "Northern", "O": "Orange", "P": "Peaceful",
    "Q": "Quiet", "R": "Rivers", "S": "Silver", "T": "Travelers",
    "U": "Under", "V": "Vivid", "W": "Wandering", "X": "Xylophones",
    "Y": "Yellow", "Z": "Zebras"
}


def hide_message(message: str) -> str:
    words = []
    for letter in message.upper():
        if letter in WORD_BANK:
            words.append(WORD_BANK[letter])
    return " ".join(words)


def reveal_message(text: str) -> str:
    letters = []
    for word in text.split():
        letters.append(word[0].upper())
    return "".join(letters)


@route
def index(state: State) -> Page:
    return Page(state, [
        Header("Steganography Game"),
        "Find messages hidden in plain sight!",
        "Enter your player name:",
        TextBox("username", state.username),
        Button("Start New Game", "start_game"),
        Link("How to Play", "instructions")
    ])


@route
def instructions(state: State) -> Page:
    return Page(state, [
        Header("How to Play"),
        "Each game gives you 3 Easy, 3 Medium, and 3 Hard puzzles, picked at random.",
        "Each puzzle hides a word using a pattern. Find it and type your guess.",
        "Hints are optional, but cut that puzzle's points in half.",
        "Easy = 10, Medium = 20, Hard = 30 points before hints.",
        "You only earn points the first time you solve each puzzle.",
        Link("Home", "index")
    ])


@route
def start_game(state: State, username: str) -> Page:
    if username.strip() == "":
        state.status = "Please enter a name first."
        return Page(state, [Header("Name required"), state.status, Button("Back", "index")])
    state.username = username.strip()
    state.score = 0
    state.current_challenge = 0
    state.challenges = create_challenges()
    state.status = "New game started."
    state.last_encoded = ""
    return challenge_list(state)


@route
def challenge_list(state: State) -> Page:
    content = [
        Header("Choose a Challenge"),
        "Player: " + state.username,
        "Score: " + str(state.score),
        "Completed: " + str(count_completed(state.challenges)) + "/9",
    ]
    options = []
    for index, challenge in enumerate(state.challenges):
        label = str(index + 1) + ": " + challenge.difficulty
        if challenge.completed:
            label += " (Completed)"
        options.append(label)
    content.extend([
        "Select a challenge:",
        SelectBox("choice", options),
        Button("Open Challenge", "select_challenge"),
        Link("My Score", "view_score"),
        Link("Encode a Message", "encode_page"),
        Link("Decode a Message", "decode_page"),
        Link("Home", "index")
    ])
    return Page(state, content)


@route
def select_challenge(state: State, choice: str) -> Page:
    # A selection looks like '4: Medium' or '4: Medium (Completed)'.
    state.current_challenge = int(choice.split(":")[0]) - 1
    return show_challenge(state)


@route
def show_challenge(state: State) -> Page:
    challenge = state.challenges[state.current_challenge]
    content = [
        Header("Challenge " + str(state.current_challenge + 1)),
        "Difficulty: " + challenge.difficulty,
        "Find the hidden word:",
        PreformattedText(challenge.encoded_text),
        "Available points: " + str(calculate_points(challenge))
    ]
    if challenge.hint_used:
        content.append("Hint: " + challenge.hint)
    elif not challenge.completed:
        content.append(Button("Reveal Hint (half points)", "use_hint"))
    if challenge.completed:
        content.append("You have already solved this challenge!")
    else:
        content.extend([
            "Your answer:",
            TextBox("answer"),
            Button("Submit Answer", "submit_answer")
        ])
    content.append(Link("Back to Challenges", "challenge_list"))
    return Page(state, content)


@route
def use_hint(state: State, answer: str = "") -> Page:
    challenge = state.challenges[state.current_challenge]
    if not challenge.completed:
        challenge.hint_used = True
    return show_challenge(state)


@route
def submit_answer(state: State, answer: str) -> Page:
    challenge = state.challenges[state.current_challenge]
    if challenge.completed:
        state.status = "You already completed this challenge."
    elif check_answer(answer, challenge.hidden_message):
        points = calculate_points(challenge)
        state.score += points
        challenge.completed = True
        state.status = "Correct! You earned " + str(points) + " points!"
    else:
        state.status = "Incorrect. Try again, or reveal the hint."
    return Page(state, [
        Header("Challenge Result"),
        state.status,
        "Total score: " + str(state.score),
        Button("Return to Challenge", "show_challenge"),
        Button("Choose Another Challenge", "challenge_list")
    ])


@route
def view_score(state: State) -> Page:
    return Page(state, [
        Header("Your Score"),
        "Player: " + state.username,
        "Total points: " + str(state.score) + " / 180",
        "Challenges completed: " + str(count_completed(state.challenges)) + " / 9",
        Link("Back to Challenges", "challenge_list"),
        Button("Play a New Random Game", "reset_game")
    ])


@route
def reset_game(state: State) -> Page:
    state.score = 0
    state.current_challenge = 0
    state.challenges = create_challenges()
    state.status = "New random challenges selected."
    state.last_encoded = ""
    return challenge_list(state)


@route
def encode_page(state: State) -> Page:
    return Page(state, [
        Header("Hide Your Own Message"),
        "Enter a word or phrase. This simple encoder uses first letters of words.",
        "Only A-Z letters are used; spaces and punctuation are ignored.",
        TextArea("secret_message", "", rows=3),
        Button("Encode", "encode_message"),
        Link("Back to Challenges", "challenge_list")
    ])


@route
def encode_message(state: State, secret_message: str) -> Page:
    encoded = hide_message(secret_message)
    if encoded == "":
        encoded = "Please enter a message containing letters A-Z."
    state.last_encoded = encoded
    return Page(state, [
        Header("Encoded Text"),
        PreformattedText(encoded),
        Button("Encode Another", "encode_page"),
        Link("Decode a Message", "decode_page"),
        Link("Back to Challenges", "challenge_list")
    ])


@route
def decode_page(state: State) -> Page:
    return Page(state, [
        Header("Decode Your Own Text"),
        "This decoder uses the first letter of each word.",
        TextArea("encoded_text", state.last_encoded, rows=4),
        Button("Decode", "decode_message"),
        Link("Back to Challenges", "challenge_list")
    ])


@route
def decode_message(state: State, encoded_text: str) -> Page:
    if encoded_text.strip() == "":
        result = "Please enter some text first."
    else:
        result = reveal_message(encoded_text)
    return Page(state, [
        Header("Decoded Message"),
        result,
        Button("Decode Another", "decode_page"),
        Link("Back to Challenges", "challenge_list")
    ])


# Bakery tests
assert_equal(check_answer(" tiger ", "TIGER"), True)
assert_equal(check_answer("dog", "CAT"), False)
assert_equal(reveal_message(hide_message("HELLO")), "HELLO")
assert_equal(count_completed(puzzle_bank()), 0)
assert_equal(len(create_challenges()), 9)
assert_equal(calculate_points(Challenge("A", "B", "Hard", False, "", True)), 15)

start_server(State("", 0, create_challenges(), 0, "", ""))


