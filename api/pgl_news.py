import json

# ---------------------
# GET API calls
# ---------------------

def GET_information_list(_query):
    response = {"list":[], "total_count":0}
    return json.dumps(response).encode()

# ---------------------
# POST API calls
# ---------------------
