import re
import requests
import random

base_api_url = "https://pokeapi.co/api/v2"
type_list = [
    "normal",
    "fighting",
    "electric",
    "fire",
    "water",
    "grass",
    "ground",
    "rock",
    "ghost",
    "steel",
    "fairy",
    "flying",
    "psychic",
    "dark",
    "dragon",
    "poison",
    "bug",
    "ice",
]

NO_MATCH_STR = "\033[107m X \033[0m"
ONE_MATCH_STR = "\033[103m ~ \033[0m"
CORRECT_STR = "\033[102m ! \033[0m"
OVERSHOT_MATCH_STR = "\033[104m ? \033[0m"
CORRECT_ANSI = "\033[92m"
WRONG_SPOT_ANSI = "\033[93m"
MISS_ANSI = "\033[91m"
RESET_ANSI = "\033[0m"


def main():
    display_startup_message()
    poke_dict = fetch_all_pokedata()
    mystery_val = choose_mystery_val(poke_dict)
    mystery_poke = mystery_val["name"]
    mystery_combo = mystery_val["types"]
    attacking_types = random.sample(type_list, 5)

    if len(mystery_combo) == 1:
        mystery_rels = [ get_monotype_relation(type, mystery_combo[0]) for type in attacking_types ]
    else:
        mystery_rels = [ get_dualtype_relation(type, mystery_combo) for type in attacking_types ]

    poke_names = [ entry["name"] for entry in poke_dict ]
    guess_hist = []

    i = 0
    while i < 6:
        user_inp = input(f"Please enter your guess ({6 - i}/6): ").lower()

        if user_inp not in poke_names:
            print(f"Invalid pokemon provided, please retry ({6 - i}/6 guesses remaining)")
            continue

        user_poke = get_poke_types(user_inp)
        user_poke_type = user_poke["types"]
        type_match_char = get_win_char(user_poke_type, mystery_combo)
        if len(user_poke_type) == 1:
            user_matchups = [ get_monotype_relation(type, user_poke_type[0]) for type in attacking_types ]
        else:
            user_matchups = [ get_dualtype_relation(type, user_poke_type) for type in attacking_types ]

        guess_hist.append({
            "name": user_inp,
            "type_match": type_match_char,
            "type1": user_poke_type[0],
            "type2": user_poke_type[1] if len(user_poke_type) == 2 else "___",
            "matchup_res": format_user_matchups(user_matchups, mystery_rels),
        })

        print(format_row("Type", "Name", "Type 1", "Type 2", attacking_types[0].capitalize(), attacking_types[1].capitalize(), attacking_types[2].capitalize(), attacking_types[3].capitalize(), attacking_types[4].capitalize()))
        for row in guess_hist:
            print(
                format_row(
                    row["type_match"],
                    row["name"].capitalize(),
                    row["type1"].capitalize(),
                    row["type2"].capitalize(),
                    f"{row['matchup_res'][0]}",
                    f"{row['matchup_res'][1]}",
                    f"{row['matchup_res'][2]}",
                    f"{row['matchup_res'][3]}",
                    f"{row['matchup_res'][4]}",
                )
            )


        if type_match_char == CORRECT_STR:
            print(f"\033[102m You won! I'd chosen \033[3m{mystery_poke.capitalize()}\033[23m as my pokemon!\033[0m")
            return

        i += 1

    print(f"\033[101m You lost! The pokemon I chose was: \033[3m{mystery_poke.capitalize()}\033[23m with the typings {mystery_combo[0].capitalize()}{f', {mystery_combo[1].capitalize()}' if len(mystery_combo) == 2 else ''}\033[0m")


def display_startup_message():
    print("Hello, welcome to my submission for CS50-Python. This is Weakdle, a game based on \033[43mPokemon\033[0m types.")
    print(f"In this game, you try to guess the type combination the game has chosen by guessing a pokemon, with {CORRECT_ANSI}6{RESET_ANSI} attempts. Just like Wordle, after \033[3meach\033[23m attempt, you'll be given the results of your guess, showing how your guessed type combination stands up defensively against 5 randomly chosen attacking types, with entries of the interactions \033[3m(0.25x, 0.5x, 1x, 2x or 4x)\033[23m will be highlighted in {MISS_ANSI}red{RESET_ANSI} (white is a bit meh looking), {CORRECT_ANSI}green{RESET_ANSI} or {WRONG_SPOT_ANSI}yellow{RESET_ANSI}, with standard meanings")
    print("Also, you'll be presented with another index, for determining how many types you're matching or missing. So here's the list:")
    print(f"{NO_MATCH_STR} - none of the guessed types are there in the mystery pokemon")
    print(f"{ONE_MATCH_STR} - one of the guessed types is there in the mystery pokemon")
    print(f"{CORRECT_STR} - you got the types of the mystery pokemon")
    print(f"{OVERSHOT_MATCH_STR} - one of the guessed types is there in the mystery pokemon, but the pokemon is monotype (has a single type)")
    print("A CLI implementation of \033[3;102mhttps://dentotino.com/weakdle\033[0m")


def strip_ansi_codes(text):
    ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', text)


def center_with_ansi(text, width):
    stripped_text = strip_ansi_codes(text)
    padding = (width - len(stripped_text)) // 2
    return ' ' * padding + text + ' ' * (width - len(stripped_text) - padding)


def format_row(type, name, type1, type2, atype1, atype2, atype3, atype4, atype5):
    return (f"{center_with_ansi(type, 5)} | {center_with_ansi(name, 30)} | "
            f"{center_with_ansi(type1, 8)} | {center_with_ansi(type2, 8)} | "
            f"{center_with_ansi(atype1, 8)} | {center_with_ansi(atype2, 8)} | "
            f"{center_with_ansi(atype3, 8)} | {center_with_ansi(atype4, 8)} | "
            f"{center_with_ansi(atype5, 8)} |")


def format_user_matchups(user_matchups, mystery_rels):
    return_data = [""] * len(user_matchups)
    mystery_rels_copy = mystery_rels.copy()

    # First pass for correct entries at correct spots
    for i in range(len(user_matchups)):
        if user_matchups[i] == mystery_rels[i]:
            return_data[i] = f"{CORRECT_ANSI}{matchup_str_format(user_matchups[i])}{RESET_ANSI}"
            mystery_rels_copy[i] = None  # Mark as used
            user_matchups[i] = None  # Mark as used

    # Second pass for correct entries at wrong spots
    for i in range(len(user_matchups)):
        if user_matchups[i] is not None:
            if user_matchups[i] in mystery_rels_copy:
                return_data[i] = f"{WRONG_SPOT_ANSI}{matchup_str_format(user_matchups[i])}{RESET_ANSI}"
                mystery_rels_copy[mystery_rels_copy.index(user_matchups[i])] = None  # Mark as used
            else:
                return_data[i] = f"{MISS_ANSI}{matchup_str_format(user_matchups[i])}{RESET_ANSI}"

    return return_data


def matchup_str_format(matchup):
    if matchup == 0.5:
        return "1/2x"
    elif matchup == 0.25:
        return "1/4x"
    else:
        return f"{int(matchup)}x"


def get_win_char(input: list[str], combo: list[str]) -> str:
    if len(combo) == 1:
        if combo[0] in input:
            if len(input) == 1:
                return CORRECT_STR
            return OVERSHOT_MATCH_STR

        return NO_MATCH_STR

    if len(input) == 1:
        if input[0] in combo:
            return ONE_MATCH_STR
        return NO_MATCH_STR

    bool1 = input[0] in combo
    bool2 = input[1] in combo

    if bool1 and bool2:
        return CORRECT_STR
    elif bool1 or bool2:
        return ONE_MATCH_STR
    return NO_MATCH_STR


def fetch_all_pokedata():
    try:
        raw = requests.get(f"{base_api_url}/pokemon/?limit=10000")
        json_content = raw.json()
        return json_content["results"]
    except Exception as err:
        raise SystemExit(err)


def choose_mystery_val(poke_dict):
    rand_poke = random.choice(poke_dict)

    return get_poke_types(rand_poke["name"])


def get_poke_types(poke_name):
    try:
        raw_poke = requests.get(f"{base_api_url}/pokemon/{poke_name}")
        types = [ type["type"]["name"] for type in raw_poke.json()["types"] ]
        return {
            "name": poke_name,
            "types": types,
        }
    except Exception as err:
        raise SystemExit(err)


def get_monotype_relation(attack_type: str, defence_type: str):
    weak_matrix = {
        "normal": ["fighting"],
        "fighting": ["flying", "psychic", "fairy"],
        "electric": ["ground"],
        "fire": ["water", "ground", "rock"],
        "water": ["electric", "grass"],
        "grass": ["fire", "ice", "poison", "flying", "bug"],
        "ground": ["water", "grass", "ice"],
        "rock": ["water", "grass", "fighting", "ground", "steel"],
        "ghost": ["ghost", "dark"],
        "steel": ["fire", "fighting", "ground"],
        "fairy": ["poison", "steel"],
        "flying": ["electric", "ice", "rock"],
        "psychic": ["bug", "ghost", "dark"],
        "dark": ["fighting", "bug", "fairy"],
        "dragon": ["dragon", "ice", "fairy"],
        "poison": ["ground", "psychic"],
        "bug": ["fire", "flying", "weak"],
        "ice": ["fire", "fighting", "rock", "steel"],
    }

    immune_matrix = {
        "normal": ["ghost"],
        "fighting": [],
        "electric": [],
        "fire": [],
        "water": [],
        "grass": [],
        "ground": ["electric"],
        "rock": [],
        "ghost": ["normal", "fighting"],
        "steel": ["poison"],
        "fairy": ["dragon"],
        "flying": ["ground"],
        "psychic": [],
        "dark": ["psychic"],
        "dragon": [],
        "poison": [],
        "bug": [],
        "ice": [],
    }

    resist_matrix = {
        "normal": [],
        "fighting": ["bug", "rock", "dark"],
        "electric": ["electric", "flying", "steel"],
        "fire": ["fire", "grass", "ice", "bug", "steel", "fairy"],
        "water": ["fire", "water", "ice", "steel"],
        "grass": ["water", "electric", "grass", "ground"],
        "ground": ["poison", "rock"],
        "rock": ["normal", "fire", "poison", "flying"],
        "ghost": ["poison", "bug"],
        "steel": ["normal", "grass", "ice", "flying", "psychic", "bug", "rock", "dragon", "steel", "fairy"],
        "fairy": ["fighting", "bug", "dark"],
        "flying": ["grass", "fighting", "bug"],
        "psychic": ["fighting", "psychic"],
        "dark": ["ghost", "dark"],
        "dragon": ["fire", "water", "electric", "grass"],
        "poison": ["grass", "fighting", "poison", "bug", "fairy"],
        "bug": ["grass", "fighting", "ground"],
        "ice": ["ice"],
    }

    if attack_type in weak_matrix[defence_type]:
        return 2
    elif attack_type in resist_matrix[defence_type]:
        return 0.5
    elif attack_type in immune_matrix[defence_type]:
        return 0
    else:
        return 1


def get_dualtype_relation(attack_type: str, defence_types: str):
    return get_monotype_relation(attack_type, defence_types[0]) * get_monotype_relation(attack_type, defence_types[1])


if __name__ == "__main__":
    main()
