import time
import json
from typing import List
from pathlib import Path
from random import randint
from enum import Enum, auto

from config import args

ROOT_DIR = Path(__file__).resolve().parent.parent

class PlayerStatus(Enum):
    AWAKE = 0
    SLEEPING = auto()
    DREAMING = auto()
    WAKE_READY = auto()

def generate_otoken():
    player_data = read_player_data()
    return f"{randint(1, 99)}dwt{player_data['member']['world_id']}{int(time.time()):x}.{randint(10000000, 99999999)}"

# player data

def read_player_data():
    with open(ROOT_DIR / "save_data" / "player_data.json", encoding="UTF-8") as f:
        return json.load(f)

def write_player_data(data: dict):
    player_data = read_player_data()
    player_data["member"].update(data)
    with open(ROOT_DIR / "save_data" / "player_data.json", "w", encoding="UTF-8") as f:
        json.dump(player_data, f, indent=2, ensure_ascii=False)

# game sync data

def read_entralink_data(param: str):
    with open(ROOT_DIR / "save_data" / "game_sync.json", encoding="UTF-8") as f:
        return json.load(f).get(param, [])

def write_entralink_data(data: List[dict], data_type: str):
    with open(ROOT_DIR / "save_data" / "game_sync.json", encoding="UTF-8") as f:
        game_sync = json.load(f)

    game_sync[data_type] = data

    with open(ROOT_DIR / "save_data" / "game_sync.json", "w", encoding="UTF-8") as f:
        json.dump(game_sync, f, indent=2, ensure_ascii=False)

def update_gamesync_status(status: PlayerStatus):
    if not args.game_sync:
        return

    game_sync_file = ROOT_DIR / "save_data" / "game_sync.json"

    if not game_sync_file.exists():
        raise FileNotFoundError("A sleeping Pokémon must be tucked to bed first.")

    write_player_data({"play_status": status.value})