import ssl
import asyncio
import websockets
import json
import utils

EVERYTHING_EVENT = json.dumps([5, "OnJsonApiEvent"])
CHAMP_SELECT_SESSION_EVENT = json.dumps([5, "OnJsonApiEvent_lol-champ-select_v1_session"])
CHAMP_SELECT_CURRENT_CHAMPION_EVENT = json.dumps([5, "OnJsonApiEvent_lol-champ-select_v1_current-champion"])


def websocket_runner(port, password, scheme):
    url = "wss://{}:{}@127.0.0.1:{}/".format('riot', password, str(port))

    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    print("Listening for champ select events...")

    async def hello():
        async with websockets.connect(url, ssl=ssl_context) as websocket:
            await websocket.send(CHAMP_SELECT_SESSION_EVENT)
            
            while(True):
                try:
                    resp = await websocket.recv()
                    if(resp.strip() != ""):
                        response = json.loads(resp)
                        print(response)
                        player_pos = response[2]["data"]["localPlayerCellId"]
                        print("Player pos: ", player_pos)
                        if(player_pos != -1):
                            phase = response[2]["data"]["timer"]["phase"]
                            is_final_pick = False
                            if(phase == "FINALIZATION"):
                                is_final_pick = True
                            else:
                                is_final_pick = response[2]["data"]["actions"][0][player_pos]["completed"]
                                
                            champ_id = response[2]["data"]["myTeam"][player_pos]["championId"]
                            assigned_role = response[2]["data"]["myTeam"][player_pos]["assignedPosition"]
                            print("Picked: {} @ {}\nFinal Pick: {}\nSelect Phase: {}\n".format(utils.get_champ_name_from_id(champ_id)[0], assigned_role, str(is_final_pick, phase)))

                            # assume champ and role are known
                            #champ = <SOME_METHOD_RETURN>
                            #role = <SOME_METHOD_RETURN>
                            #update_best_runes(champion, role)

                except json.decoder.JSONDecodeError as e:
                    pass


    asyncio.get_event_loop().run_until_complete(hello())
    asyncio.get_event_loop().run_forever()