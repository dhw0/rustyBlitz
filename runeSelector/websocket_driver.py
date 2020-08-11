from driver import RuneSelector
import ssl
import asyncio
import websockets
import json
import utils

rs = RuneSelector("/mnt/g/games/LeagueOfLegends/League of Legends/lockfile")
url = "wss://{}:{}@127.0.0.1:{}/".format('riot', rs.password, str(rs.port))
print(url)

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

#sub2 = "[5, \"OnJsonApiEvent\", {}]"
sub2 = json.dumps([5, "OnJsonApiEvent"])
#sub = json.dumps([5, "OnJsonApiEvent_lol-champ-select_v1_session"])
sub = json.dumps([5, "OnJsonApiEvent_lol-champ-select_v1_current-champion"])

async def hello():
    async with websockets.connect(url, ssl=ssl_context) as websocket:
        await websocket.send(sub)
		
        while(True):
            resp = await websocket.recv()
            if(resp.strip() != ""):
                response = json.loads(resp)
                print(response)
                #champ_id = response[2]["data"]["actions"][0][0]["championId"]
                #is_final_pick = response[2]["data"]["actions"][0][0]["completed"]
                #print("Picked: {}, is final?: {}".format(utils.get_champ_name_from_id(champ_id)[0], str(is_final_pick)))

asyncio.get_event_loop().run_until_complete(hello())
asyncio.get_event_loop().run_forever()
