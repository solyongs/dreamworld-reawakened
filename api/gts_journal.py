import json

# ---------------------
# GET API calls
# ---------------------

def GET_trade_list(_query):
    result = {"trade_list":[]}
    
    # Dummy data
    dummy_trade1 = {
        "trade1": {
          "country_id": 220,
          "country_name": "United States of America",
          "monsno": 644,
          "form_no": 0,
          "poke_level": 100,
          "sex": 2 
        },
        "trade2": {
          "country_id": 105,
          "country_name": "Japan",
          "monsno": 643,
          "form_no": 0,
          "poke_level": 100,
          "sex": 2
        }
    }
    
    # Test gender icons
    dummy_trade2 = {
        "trade1": {
          "country_id": 170,
          "country_name": "South Korea",
          "monsno": 628,
          "form_no": 0,
          "poke_level": 54,
          "sex": 0 
        },
        "trade2": {
          "country_id": 195,
          "country_name": "Spain",
          "monsno": 630,
          "form_no": 0,
          "poke_level": 54,
          "sex": 1
        }
    }
    
    result["trade_list"].append(dummy_trade1)
    result["trade_list"].append(dummy_trade2)
    return json.dumps(result).encode()

# ---------------------
# POST API calls
# ---------------------
