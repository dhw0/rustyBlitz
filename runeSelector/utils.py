import json
import requests
import psutil
from subprocess import check_output

def load_data_dragon_runes(ddpath):
    with open(ddpath, 'r') as f:
        data = json.load(f)
    return data


def get_champ_name_from_id(champ_id, patch="10.16"):
    url = "https://raw.communitydragon.org/{}/plugins/rcp-be-lol-game-data/global/default/v1/champions/{}.json".format(patch, str(champ_id))
    r = requests.get(url).json()
    return r["name"], r["alias"]


def get_lockfile_data(lockfile_path):
    with open(lockfile_path, 'r') as f:
        data = f.readline().strip().split(':')
        # port, password, scheme
        return data[2], data[3], data[4]


def find_process_with_name_bash(process_name):
    out = check_output(["wmic.exe", "process", "where", "caption=\"test.exe\"", "get", "commandline"])
    print(out)