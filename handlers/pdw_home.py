#!/usr/bin/env python3
import json
import time
import psutil
import utility
from random import choice, randint

# ---------------------
# GET API calls
# ---------------------

def GET_board_pokemon_list(_query):
    print(json.dumps(_query, indent=2))

    return b'{}'


def GET_footprint_list(_query):
    footprint_list = {"list":[]}

    valid_footprints = [598,25,85,623,2,32,183,428,648,636,616,609,594,593,574,564,558,547,543,520,518,491,474,421,420,406,121,120,13,10,647]

    for _ in range(10):
        pkmn = utility.get_random_pokemon(valid_footprints)
        footprint = {
            "is_pdw": randint(0, 1),
            "is_gts": randint(0, 1),
            "is_ds": randint(0, 1),
            "friend_type": randint(0, 2),
            "updated_at": "2026/05/06 22:00",
            "pokemon_nickname": "pokemon_nickname",
            "pokemon_name": utility.lookup_str("pokemon", pkmn["pokemon_no"]),
            "pgl_name": "pgl_name",
            "pokemon_no": pkmn["pokemon_no"],
            "form_no": pkmn.get("form_no", 0), #below this is used for the popup menu
            "oyaname": "oyaname",
            "level": pkmn["level"],
            "type1": utility.lookup_str("type", pkmn["type1"]),
            "type2": utility.lookup_str("type", pkmn["type2"]),
            "sex_id": choice(pkmn["gender_ratio"]),
            "personality": utility.lookup_str("nature", randint(0, 24)),
            "exchange_flag": randint(0, 1),
            "water_flag": randint(0, 1)
        }
        footprint_list["list"].append(footprint)

    return json.dumps(footprint_list).encode()


def GET_my_bridge(_query):
    return b'{}'


def GET_my_island(_query):
    pkmn = utility.sleeping_pokemon

    response = {
        "pokemon":                {**pkmn},
        "island_id":               201,
        "point":                   0,
        "trial_flag":              0,
        "arranged_interior_list":  [{"my_interior_id":1,"interior_id":1,"x":10,"y":10,"interior_size":1,"interior_category_id":1,"rotation":0}],
        "requested_flag":          False,
        "shelf_id":                301
    }
    return json.dumps(response).encode()


def GET_my_island_area(_query):
    player_data = utility.read_player_data()

    friend_list = []
    for _ in range(5):
        friend = {
            "pgl_name": "OtherPlayerName",
            "member_id": randint(1,50000),
            "member_savedata_id": randint(1,50000),
            "island_id": 201,
            "country_id": 220,
            "is_ds": randint(0, 1),
            "is_gts": randint(0, 1),
            "is_pdw": randint(0, 1)
        }
        friend_list.append(friend)
    response = {
        "island_id": player_data["member"]["island_id"],
        "friend_list": friend_list
    }

    return(json.dumps(response).encode())


def GET_pdw_end(_query):
    for proc in psutil.process_iter():
        if "flashplayer" in proc.name():
            proc.kill()

    return b'{}'

# ---------------------
# POST API calls
# ---------------------

def POST_pdw_start(_query):
    response = {"started_at": int(time.time())}
    return json.dumps(response).encode()


def POST_pdw_timecheck(_query):
    return b'{}'