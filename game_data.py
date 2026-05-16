#!/usr/bin/env python3
import json
import time
from pathlib import Path
from random import choice
from random import randint
from datetime import datetime

ROOT_DIR = Path(__file__).resolve().parent

# --------------------
# Helper data
# --------------------

with open(ROOT_DIR / "json_data" / "items.json", encoding="UTF-8") as f:
    item_info = json.load(f)

with open(ROOT_DIR / "json_data" / "pokemon.json", encoding="UTF-8") as f:
    pokemon_info = json.load(f)

with open(ROOT_DIR / "json_data" / "dream_islands.json", encoding="UTF-8") as f:
    area_info = json.load(f)

with open(ROOT_DIR / "json_data" / "berries.json", encoding="UTF-8") as f:
    berry_data = json.load(f)

pokemon_natures = ("Adamant","Bashful","Bold","Brave","Calm","Careful","Docile","Gentle","Hardy","Hasty","Impish","Jolly","Lax","Lonely","Mild","Modest","Naive","Naughty","Quiet","Quirky","Rash","Relaxed","Sassy","Serious","Timid")

# --------------------
# Helper functions
# --------------------

def generate_otoken():
    return f"{randint(1, 99)}dwt{player_data['member']['world_id']}{int(time.time()):x}.{randint(10000000, 99999999)}"

def date_to_unix(datetime_string: str):
    return datetime.strptime(datetime_string, "%Y-%m-%d").timestamp()

def get_random_pokemon(restriction_list: list[int] | None = None) -> dict[str: str|None]:
    if restriction_list is None:
        pkmn_options = [i for i in list(pokemon_info)]
    else:
        pkmn_options = [i for i in list(pokemon_info) if int(i.split("-")[0]) in restriction_list]

    pkmn = choice(pkmn_options)
    natdex = pkmn.split("-")[0]

    return {**pokemon_info[pkmn], "pokemon_no": natdex}

# --------------------
# Save data manager classes
# --------------------

class ChestManager:
    def __init__(self, data_path):
        self.path = data_path
        with open(self.path, encoding="UTF-8") as f:
            self.data = json.load(f)

    def save(self):
        with open(self.path, "w", encoding="UTF-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def fetch_item_by_id(self, item_id):
        return next((item for item in self.data["list"] if item["pokeitem_id"] == item_id), None)

    def add_item(self, item_id, count):
        current_date = datetime.now().strftime("%Y-%m-%d")

        chest_item = self.fetch_item_by_id(item_id)

        if chest_item:
            chest_item["item_cnt"] += count
            chest_item["date"] = current_date

        else:
            curr_item_info = item_info[str(item_id)]
            self.data["cnt"] += 1
            new_item = {
                "pokeitem_id": item_id,
                "pokeitem": curr_item_info["item_name"],
                "item_cnt": count,
                "bunrui_no": curr_item_info["first_sort"],
                "b_hozon_sentou": curr_item_info["second_sort"],
                "date": current_date,
                "field_line1": curr_item_info["desc"][0],
                "field_line2": curr_item_info["desc"][1],
                "field_line3": curr_item_info["desc"][2]
            }
            self.data["list"].append(new_item)

        self.save()

    def remove_item(self, item_id, count):
        current_date = datetime.now().strftime("%Y-%m-%d")
        chest_item = self.fetch_item_by_id(int(item_id))

        chest_item["item_cnt"] -= count
        chest_item["date"] = current_date

        if chest_item["item_cnt"] <= 0:
            item_index = self.data["list"].index(chest_item)
            del self.data["list"][item_index]
            self.data["cnt"] -= 1

        self.save()


class CropManager:
    def __init__(self, data_path):
        self.path = data_path
        with open(self.path, encoding="UTF-8") as f:
            self.data = json.load(f)

    def save(self):
        with open(self.path, "w", encoding="UTF-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def fetch_plot_by_id(self, my_croft_id):
        return next((p for p in self.data["croft_list"] if p["my_croft_id"] == my_croft_id), None)
    
    def water_plot(self, my_croft_id):
        plot = self.fetch_plot_by_id(my_croft_id)
        plot["dirt_hp"] = 100

        self.save()

    def sow(self, my_croft_id, pokeitem_id):
        plot = self.fetch_plot_by_id(my_croft_id)

        current_time = round(time.time())

        berry_id = int(pokeitem_id) - 148

        plot.update({
            "my_croft_id": my_croft_id,
            "pokeitem_id": int(pokeitem_id),
            "kinomi": item_info[pokeitem_id]["item_name"],
            "kinomi_id": berry_id,
            "dirt_hp": 100,
            "desc1": item_info[pokeitem_id]["desc"][0],
            "desc2": item_info[pokeitem_id]["desc"][1],
            "desc3": item_info[pokeitem_id]["desc"][2],
            "kinomi_state": 0,
            "x": plot["x"],
            "y": plot["y"],
            "server": {"planted_time": current_time, "last_update_time": current_time, "yield": berry_data[str(berry_id)]["max_yield"]}
        })

        self.save()

    def harvest(self, my_croft_id):
        plot = self.fetch_plot_by_id(my_croft_id)
        plot_index = self.data["croft_list"].index(plot)
        
        harvest_data = {
            "kinomi_id": plot["kinomi_id"],
            "kinomi": plot["kinomi"],
            "pokeitem_id": plot["pokeitem_id"],
            "count": plot["server"]["yield"]
        }
        
        self.data["croft_list"][plot_index] = {"my_croft_id": my_croft_id, "x": plot["x"], "y": plot["y"]}
        
        self.save()

        return harvest_data
    
    def process_berry_growth(self):
        current_time = round(time.time())

        for plant in self.data["croft_list"]:
            if "dirt_hp" not in plant:
                continue

            curr_berry_data = berry_data[str(plant["kinomi_id"])]

            hours_since_planted = (current_time - plant["server"]["planted_time"]) // 3600
            hours_since_update = (current_time - plant["server"]["last_update_time"]) // 3600

            hours_at_last_update = hours_since_planted - hours_since_update

            single_stage_time = curr_berry_data["grow_time"] / 4

            for hour in range(1, hours_since_update + 1):
                total_hours = hours_at_last_update + hour
                plant["kinomi_state"] = min(total_hours // single_stage_time, 4)

                if plant["dirt_hp"] == 0: #remove 1/5th of the berry's max, but no lower than 2 berries
                    plant["server"]["yield"] = max(plant["server"]["yield"] - (curr_berry_data["max_yield"] * 0.2), 2)
                else:
                    plant["dirt_hp"] -= curr_berry_data["drain_rate"]
            
            if plant["dirt_hp"] < 0:
                plant["dirt_hp"] = 0

            plant["server"]["last_update_time"] = current_time

        self.save()
    
# --------------------
# Save data
# --------------------

with open(ROOT_DIR / "save_data" / "player_data.json", encoding="UTF-8") as f:
    player_data = json.load(f)

with open(ROOT_DIR / "save_data" / "sleeping_pokemon.json", encoding="UTF-8") as f:
    sleeping_pokemon = json.load(f)

chest = ChestManager(ROOT_DIR / "save_data" / "chest_data.json")

crops = CropManager(ROOT_DIR / "save_data" / "crop_data.json")

# --------------------
# Manage Entralinked data
# --------------------

def write_entralinked_data(entralinked_dir):
    version_language = {
        "WHITE_JAPANESE": (20, 1, "ポケットモンスター ホワイト"),
        "WHITE_ENGLISH":  (20, 2, "Pokémon White Version"),
        "WHITE_FRENCH":   (20, 3, "Pokémon Version Blanche"),
        "WHITE_ITALIAN":  (20, 4, "Pokémon Versione Bianca"),
        "WHITE_GERMAN":   (20, 5, "Pokémon Weiße Edition"),
        "WHITE_SPANISH":  (20, 7, "Pokémon Edición Blanca"),
        "WHITE_KOREAN":   (20, 8, "포켓몬스터 화이트"),

        "BLACK_JAPANESE": (21, 1, "ポケットモンスター ブラック"),
        "BLACK_ENGLISH":  (21, 2, "Pokémon Black Version"),
        "BLACK_FRENCH":   (21, 3, "Pokémon Version Noire"),
        "BLACK_ITALIAN":  (21, 4, "Pokémon Versione Nera"),
        "BLACK_GERMAN":   (21, 5, "Pokémon Schwarze Edition"),
        "BLACK_SPANISH":  (21, 7, "Pokémon Edición Negra"),
        "BLACK_KOREAN":   (21, 8, "포켓몬스터 블랙"),

        "WHITE_2_JAPANESE": (22, 1, "ポケットモンスター ホワイト２"),
        "WHITE_2_ENGLISH":  (22, 2, "Pokémon White Version 2"),
        "WHITE_2_FRENCH":   (22, 3, "Pokémon Version Blanche 2"),
        "WHITE_2_ITALIAN":  (22, 4, "Pokémon Versione Bianca 2"),
        "WHITE_2_GERMAN":   (22, 5, "Pokémon Weiße Edition 2"),
        "WHITE_2_SPANISH":  (22, 7, "Pokémon Edición Blanca 2"),
        "WHITE_2_KOREAN":   (22, 8, "포켓몬스터 화이트2"),

        "BLACK_2_JAPANESE": (23, 1, "ポケットモンスター ブラック２"),
        "BLACK_2_ENGLISH":  (23, 2, "Pokémon Black Version 2"),
        "BLACK_2_FRENCH":   (23, 3, "Pokémon Version Noire 2"),
        "BLACK_2_ITALIAN":  (23, 4, "Pokémon Versione Nera 2"),
        "BLACK_2_GERMAN":   (23, 5, "Pokémon Schwarze Edition 2"),
        "BLACK_2_SPANISH":  (23, 7, "Pokémon Edición Negra 2"),
        "BLACK_2_KOREAN":   (23, 8, "포켓몬스터 블랙2")
    }

    with open(Path(entralinked_dir) / "data.json", "r") as f:
        data = json.load(f)

    rom_id, langcode, rom_name = version_language[data["gameVersion"]]

    form_str = ""
    pkmn_species = data['dreamerInfo']['species']
    pkmn_form = data["dreamerInfo"]["form"]
    if pkmn_form:
        form_num = next(k.split("-")[1] for k, v in pokemon_info.items() if v.get("form_no", "0") == str(pkmn_form) and str(pkmn_species) in k)
        form_str = f"-{form_num}"
    
    pkmn_info = pokemon_info[f"{pkmn_species}{form_str}"]

    player_data["member"].update({ 
        "send_pokemon_count": player_data["member"]["send_pokemon_count"] + 1,
        "rom_id":             rom_id,
        "rom_name":           rom_name,
        #"player_badge_num":   "8",          #not currently tracked by Entralinked
        #"alter_rom_name":     "PlayerName", #not currently tracked by Entralinked
        "langcode":           langcode,
        "pokemon_no":         str(data["dreamerInfo"]["species"]),
        "pokemon_name":       pkmn_info["pokemon_name"],
        "form_no":            str(data["dreamerInfo"]["form"]),
        "type1":              pkmn_info["type1"],
        "type2":              pkmn_info["type2"],
        "gscd":               data["gameSyncId"]
    })

    pkmn_gender = (0 if data["dreamerInfo"]["gender"] == "MALE" else
                   1 if data["dreamerInfo"]["gender"] == "FEMALE" else 2)

    sleeping_pokemon.update({
        "pokemon_no":        data["dreamerInfo"]["species"],
        "pokemon_name":      pkmn_info["pokemon_name"],
        "form_no":           str(data["dreamerInfo"]["form"]),
        "type1":             pkmn_info["type1"],
        "type2":             pkmn_info["type2"],
        "pokemon_nickname":  data["dreamerInfo"]["nickname"] if data["dreamerInfo"]["nickname"] != pkmn_info["pokemon_name"] else None,
        "oyaname":           data["dreamerInfo"]["trainerName"],
        "level":             data["dreamerInfo"]["level"],
        "sex":               pkmn_gender,
        "personality":       data["dreamerInfo"]["nature"].title(),
        #"ball_name":        "Cherish Ball" #not currently tracked by Entralinked
    })

    with open(ROOT_DIR / "save_data" / "player_data.json", "w", encoding="UTF-8") as f:
        json.dump(player_data, f, indent=2, ensure_ascii=False)

    with open(ROOT_DIR / "save_data" / "sleeping_pokemon.json", "w", encoding="UTF-8") as f:
        json.dump(sleeping_pokemon, f, indent=2, ensure_ascii=False)


def init_entralinked():
    entralinked_config = ROOT_DIR / "json_data" / "entralinked.json"

    if entralinked_config.exists():
        with open(entralinked_config, "r") as f:
            config = json.load(f)
            entralinked_dir = config["entralinked_dir"]
            print("ENTRALINKED: Loaded Entralinked path")

        return entralinked_dir

    else:
        import tkinter as tk
        from tkinter.filedialog import askdirectory

        root = tk.Tk()
        root.withdraw()

        print("ENTRALINKED: Select the folder that contains entralinked.jar")
        entralink_root_dir = askdirectory(title="Select the folder that contains entralinked.jar")
        
        print("ENTRALINKED: Select the folder that corresponds to the Game Sync code")
        entralinked_dir = askdirectory(title="Select the folder that corresponds to the Game Sync code", initialdir=Path(entralink_root_dir) / "players")

        if Path(entralinked_dir).parts[-2] != "players":
            print("ENTRALINKED: Error selecting Entralinked data folder. Starting server normally.")
            return
        
        with open(entralinked_config, "w+") as f:
            json.dump({"entralinked_dir":entralinked_dir}, f, indent=2)
            print("ENTRALINKED: Saved Entralinked path")

        return entralinked_dir