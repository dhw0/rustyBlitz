import ssl
import asyncio
import websockets
import json
import utils
from driver import fully_manual_rune_select

SUBSCRIBE = 5

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

EVERYTHING_EVENT = json.dumps([SUBSCRIBE, "OnJsonApiEvent"])
SUB_CHAMP_SELECT_SESSION_EVENT = json.dumps([SUBSCRIBE, "OnJsonApiEvent_lol-champ-select_v1_session"])
CHAMP_SELECT_CURRENT_CHAMPION_EVENT = json.dumps([SUBSCRIBE, "OnJsonApiEvent_lol-champ-select_v1_current-champion"])

def get_data_from_response(response):
    player_pos = response[2]["data"]["localPlayerCellId"]%5
    if(player_pos != -1):
        phase = response[2]["data"]["timer"]["phase"]
        is_final_pick = False
        if(phase == "FINALIZATION" or len(response[2]["data"]["actions"]) == 0):
            is_final_pick = True
        else:
            is_final_pick = response[2]["data"]["actions"][0][player_pos]["completed"]

        champ_id = response[2]["data"]["myTeam"][player_pos]["championId"]
        assigned_role = response[2]["data"]["myTeam"][player_pos]["assignedPosition"]
    
    return player_pos, champ_id, assigned_role, phase, is_final_pick


def websocket_runner(lockfile_data):
    password = lockfile_data[1]
    port = lockfile_data[0]
    url = "wss://{}:{}@127.0.0.1:{}/".format('riot', password, str(port))
    print("Listening for champ select events...")

    async def hello():
        async with websockets.connect(url, ssl=ssl_context) as websocket:
            await websocket.send(SUB_CHAMP_SELECT_SESSION_EVENT)
            prev_champ_role = ("", "")
            while(True):
                try:
                    resp = await websocket.recv()
                    if(resp.strip() != ""):

                        response = json.loads(resp)
                        if(response[2]['eventType'] == "Update"):
                            player_pos, champ_id, assigned_role, phase, is_final_pick = get_data_from_response(response)
                            champ_name = utils.get_champ_name_from_id(champ_id)[0]

                            if(is_final_pick == True and prev_champ_role != (champ_name, assigned_role)):
                                print("Finalized pick:\n\tChamp: {}\n\tRole: {}".format(champ_name, assigned_role))
                                prev_champ_role = (champ_name, assigned_role)
                                fully_manual_rune_select(lockfile_data, champ_name, assigned_role, no_confirm=True)

                except json.decoder.JSONDecodeError as e:
                    pass


    asyncio.get_event_loop().run_until_complete(hello())
    asyncio.get_event_loop().run_forever()
