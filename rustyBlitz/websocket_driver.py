import ssl
import asyncio
import websockets
import json
import utils
from driver import update_best_runes

EVERYTHING_EVENT = json.dumps([5, "OnJsonApiEvent"])
CHAMP_SELECT_SESSION_EVENT = json.dumps([5, "OnJsonApiEvent_lol-champ-select_v1_session"])
CHAMP_SELECT_CURRENT_CHAMPION_EVENT = json.dumps([5, "OnJsonApiEvent_lol-champ-select_v1_current-champion"])


def main():
    port, password, _ = utils.get_lockfile_data("/mnt/g/games/LeagueOfLegends/League of Legends/lockfile")
    url = "wss://{}:{}@127.0.0.1:{}/".format('riot', password, str(port))

    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    async def hello():
        async with websockets.connect(url, ssl=ssl_context) as websocket:
            await websocket.send(CHAMP_SELECT_CURRENT_CHAMPION_EVENT)
            
            while(True):
                resp = await websocket.recv()
                if(resp.strip() != ""):
                    response = json.loads(resp)
                    #print(response)
                    #champ_id = response[2]["data"]["actions"][0][0]["championId"]
                    #is_final_pick = response[2]["data"]["actions"][0][0]["completed"]
                    #print("Picked: {}, is final?: {}".format(utils.get_champ_name_from_id(champ_id)[0], str(is_final_pick)))

                    # assume champ and role are known
                    champ = <SOME_METHOD_RETURN>
                    role = <SOME_METHOD_RETURN>

                    update_best_runes(champion, role)


    asyncio.get_event_loop().run_until_complete(hello())
    asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    main()