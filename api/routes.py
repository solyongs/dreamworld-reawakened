from api import (
    hb,
    pdw_croft,
    pdw_dreamland,
    pdw_home,
    pdw_item,
    pgl_member,
    pgl_news,
    pgl_top
)

GET_RESPONSES = {
    "hb":                          hb.GET_hb,
    "pdw.croft.my_croft_list":     pdw_croft.GET_my_croft_list,
    "pdw.croft.tutorial_end":      pdw_croft.GET_tutorial_end,
    "pdw.croft.tutorial_start":    pdw_croft.GET_tutorial_start,
    "pdw.croft.waterpot_list":     pdw_croft.GET_waterpot_list,
    "pdw.dreamland.top":           pdw_dreamland.GET_top,
    "pdw.dreamland.tree_top":      pdw_dreamland.GET_tree_top,
    "pdw.home.board_pokemon_list": pdw_home.GET_board_pokemon_list,
    "pdw.home.footprint_list":     pdw_home.GET_footprint_list,
    "pdw.home.my_bridge":          pdw_home.GET_my_bridge,
    "pdw.home.my_island":          pdw_home.GET_my_island,
    "pdw.home.my_island_area":     pdw_home.GET_my_island_area,
    "pdw.home.pdw_end":            pdw_home.GET_pdw_end,
    "pdw.item.item_list":          pdw_item.GET_item_list,
    "pgl.member.profile.my_state": pgl_member.GET_profile_my_state,
    "pgl.news.information_list":   pgl_news.GET_information_list,
    "pgl.top.init":                pgl_top.GET_init
}

POST_RESPONSES = {
    "pdw.croft.kinomi_harvesting":   pdw_croft.POST_kinomi_harvesting,
    "pdw.croft.kinomi_sowing":       pdw_croft.POST_kinomi_sowing,
    "pdw.croft.kinomi_watering":     pdw_croft.POST_kinomi_watering,
    "pdw.croft.waterpot_list":       pdw_croft.POST_waterpot_list,
    "pdw.dreamland.game_clear":      pdw_dreamland.POST_game_clear,
    "pdw.home.pdw_start":            pdw_home.POST_pdw_start,
    "pdw.home.pdw_timecheck":        pdw_home.POST_pdw_timecheck,
    "pdw.item.item_delivery_update": pdw_item.POST_item_delivery_update,
    "pdw.item.item_trade_list":      pdw_item.POST_item_trade_list,
    "pgl.member.profile.pdw_login":  pgl_member.POST_profile_pdw_login
}