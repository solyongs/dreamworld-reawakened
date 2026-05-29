import json
from pathlib import Path
from random import choice

ROOT_DIR = Path(__file__).resolve().parent.parent

with open(ROOT_DIR / "json_data" / "pokemon.json", encoding="UTF-8") as f:
    pokemon_info = json.load(f)

with open(ROOT_DIR / "json_data" / "dream_islands.json", encoding="UTF-8") as f:
    area_info = json.load(f)

with open(ROOT_DIR / "save_data" / "sleeping_pokemon.json", encoding="UTF-8") as f:
    sleeping_pokemon = json.load(f)

def get_random_pokemon(restriction_list: list[int] | None = None) -> dict[str: str|None]:
    """Retrieves a random Pokémon's data from `pokemon.json`.

    Args:
        restriction_list: An optional list of National Dex numbers to restrict
            the pool of possible Pokémon. If None, all Pokémon are eligible.

    Returns:
        A dictionary containing the randomly selected Pokémon's data.
        National Dex number is included as 'pokemon_no'.
    """

    if restriction_list is None:
        pkmn_options = [i for i in list(pokemon_info)]
    else:
        pkmn_options = [i for i in list(pokemon_info) if int(i.split("-")[0]) in restriction_list]

    pkmn = choice(pkmn_options)
    natdex = pkmn.split("-")[0]

    return {**pokemon_info[pkmn], "pokemon_no": natdex}