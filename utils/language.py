from utils import save_data

language_index = {
    1: "ja",
    2: "en",
    3: "fr",
    4: "it",
    5: "de",
    7: "es",
    8: "ko"
}

player_language = language_index[save_data.read_player_data()["member"]["langcode"]]