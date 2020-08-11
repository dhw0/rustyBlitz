from driver import RuneSelector
import ssl
import asyncio
import websockets

rs = RuneSelector("/mnt/g/games/LeagueOfLegends/League of Legends/lockfile")
#url = "wss://{}:{}@127.0.0.1:{}/".format('riot', rs.password, str(rs.port))
url = "wss://127.0.0.1:{}/".format(str(rs.port))
print(url)


ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

async def hello():
    async with websockets.connect(url, ssl=ssl_context, extra_headers=[("Authorization", "Basic cmlvdDpRQWpIdkl6YW5vdVc3UWFIVTB1V1Rn")]) as websocket:
        await websocket.send("[5, \"OnJsonApiEvent\"]")
		
        while(True):
            response = await websocket.recv()
            print(response)

asyncio.get_event_loop().run_until_complete(hello())
asyncio.get_event_loop().run_forever()