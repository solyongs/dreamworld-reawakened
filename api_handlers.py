import time
import json
import logging
from random import randint
from random import choice

with open("./json_data/items.json") as f:
	item_info = json.load(f)

with open("./json_data/pokemon.json") as f:
	pokemon_info = json.load(f)

pokemon_natures = ("Adamant","Bashful","Bold","Brave","Calm","Careful","Docile","Gentle","Hardy","Hasty","Impish","Jolly","Lax","Lonely","Mild","Modest","Naive","Naughty","Quiet","Quirky","Rash","Relaxed","Sassy","Serious","Timid")

# --------------------
# Static API responses
# --------------------

STATIC_GET_RESPONSES = {
    "pgl.news.information_list":   b'{"list":[], "total_count":0}',
    "pgl.member.profile.my_state": b"{}",
    "pgl.top.init":                b"{}",
    "pdw.home.my_bridge":          b"{}",
    "pdw.croft.tutorial_start":    b"{}",
    "pdw.croft.tutorial_end":      b"{}",
}

STATIC_POST_RESPONSES = {
    "pdw.home.pdw_timecheck":        b"{}",
    "pgl.member.profile.pdw_login":  b"{}",
}

# ---------------------
# Dynamic API responses
# ---------------------

def handle_my_croft_list(_query):
    croft_template = {
        "kinomi_state": 0,
        "my_croft_id":  0,
        "pokeitem_id":  0,
        "kinomi":       0,
        "kinomi_id":    52,
        "dirt_hp":      0,
    }
    response = {
        "croft_list": [
            {**croft_template, "x": 1, "y": 1},
            {**croft_template, "x": 2, "y": 1},
        ],
        "diglett_flag": 0,
    }
    return json.dumps(response).encode()


def handle_dreamland_top(_query):
    response = {
        "dreamland_area_id": randint(3, 9),
        "object_list": [],
    }
    return json.dumps(response).encode()


def handle_dreamland_tree_top(_query):
    count = randint(1, 10)

    pokemon_list = []
    encount_list = []
    
    for _ in range(count):
        pkmn = choice(list(pokemon_info.keys()))
        natdex = pkmn.split("-")[0]
        
        pkmn = pokemon_info[pkmn]

        pokemon_list.append({
            "pokemon_no":        natdex,
            "form_no":           pkmn["form_no"],
            "pgl_name":          "PGLName",
            "member_savedata_id": 123,
            "nickname":          None,
            "pokename":          pkmn["pokemon"],
            "oyaname":           "PlayerName",
            "level":             randint(1, 100),
            "type1":             pkmn["type1"],
            "type2":             pkmn["type2"],
            "sex_id":            0,
            "pokekaku":          choice(pokemon_natures),
            "pokeplace":         "Route 1",
            "ball_name":         "Poke Ball"
        }
    )   

    encount_list = []
    
    response = {"pokemon_list": pokemon_list, "encount_list": encount_list}
    logging.info("tree_top response: %s", json.dumps(response))
    return json.dumps(response).encode()


def handle_item_list(_query):
    '''Loads random items into the Treasure Chest'''
    item_list = []
    for _ in range(randint(1, 10)):
        item_id = choice(list(item_info.keys()))
        item_name = item_info.get(item_id, "TODO")["item_name"]
        item_list.append(
            {
                "pokeitem_id": int(item_id),
                "pokeitem": item_name,
                "item_cnt": str(randint(1, 99)),
                "bunrui_no": "1", #for sorting
                "b_hozon_sentou": "1", #for sorting
                "date": "2026-05-03"
            }
        )
    response = {"cnt": str(len(item_list)), "list": item_list}
    return json.dumps(response).encode()


def handle_my_island(_query):
    pkmn = choice(list(pokemon_info.keys()))
    natdex = pkmn.split("-")[0]
    
    pkmn = pokemon_info[pkmn]

    response = {
        "pokemon": {
            "pokemon_no":        natdex,
            "pokemon_name":      pkmn["pokemon"],
            "form_no":           pkmn["form_no"],
            "type1":             pkmn["type1"],
            "type2":             pkmn["type2"],
            "pokemon_nickname":  None,
            "oyaname":           "PlayerName",
            "level":             randint(1, 100),
            "sex":               randint(0, 1),
            "personality":       choice(pokemon_natures),
            "place":             "PlayerName's Island",
            "ball_name":         "Poke Ball"
        },
        "island_id":               201,
        "point":                   0,
        "trial_flag":              0,
        "arranged_interior_list":  [{"my_interior_id":1,"interior_id":1,"x":10,"y":10,"interior_size":1,"interior_category_id":1,"rotation":0}],
        "requested_flag":          False,
        "shelf_id":                301
    }
    return json.dumps(response).encode()



def handle_pdw_start(_query):
    return json.dumps({"started_at": int(time.time())}).encode()


DYNAMIC_GET_RESPONSES = {
    "pdw.croft.my_croft_list":   handle_my_croft_list,
    "pdw.dreamland.top":         handle_dreamland_top,
    "pdw.dreamland.tree_top":    handle_dreamland_tree_top,
    "pdw.item.item_list":        handle_item_list,
    "pdw.home.my_island":        handle_my_island,
}

DYNAMIC_POST_RESPONSES = {
    "pdw.home.pdw_start": handle_pdw_start,
}