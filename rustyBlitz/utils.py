import json
import requests
from subprocess import check_output
import pathlib
import sys
import os

curr_dir_path = pathlib.Path(os.path.dirname(os.path.abspath(__file__)))
data_directory = str(curr_dir_path.parent) + "/data"
sys.path.append(data_directory)

CURR_PATCH = "latest" # "10.23"

def load_data_dragon_runes(ddpath):
    with open(ddpath, 'r') as f:
        data = json.load(f)
    return data

def get_champ_name_from_id(champ_id, patch = CURR_PATCH):
    url = "https://raw.communitydragon.org/{}/plugins/rcp-be-lol-game-data/global/default/v1/champions/{}.json".format(patch, str(champ_id))
    r = requests.get(url).json()
    return r["name"], r["alias"]


def get_lockfile_data(lockfile_path):
    with open(lockfile_path, 'r') as f:
        data = f.readline().strip().split(':')
        # port, password, scheme
        return data[2], data[3], data[4]


def find_process_with_name_bash(process_name):
    try:
        out = check_output(["wmic.exe", "process", "where", "caption=\"{}\"".format(process_name), "get", "executablepath"]).decode(sys.stdout.encoding)
        raw_windows_path = out.strip().split("\n")[1].strip()
        posix_path = check_output(["wslpath", "-a", raw_windows_path]).decode(sys.stdout.encoding)
        root_league_dir = pathlib.Path(posix_path.strip()).parent
        return root_league_dir
    except:
        return ""

def get_rune_dict(patch = CURR_PATCH):
    data_file_name = "rune_data.json"
    if(not pathlib.Path(data_directory+"/"+data_file_name).is_file()):
        print('Getting new rune dictionary...')
        url = "https://raw.communitydragon.org/{}/plugins/rcp-be-lol-game-data/global/default/v1/perks.json".format(patch)
        r = requests.get(url).json()
        d = {"name_to_id":{}, "id_to_name":{}}
        for item in r:
            item_id = int(item['id'])
            cleaned_name = ''.join(e for e in item['name'] if e.isalnum()).lower()
            d['name_to_id'][cleaned_name] = item_id
            tmp = {"formatted": cleaned_name, "detailed_name":item['name']}
            d['id_to_name'][item_id] = tmp

        url2 = "https://raw.communitydragon.org/{}/plugins/rcp-be-lol-game-data/global/default/v1/perkstyles.json".format(patch)
        r = requests.get(url2).json()
        styles = r['styles']
        for item in styles:
            item_id = int(item['id'])
            cleaned_name = ''.join(e for e in item['name'] if e.isalnum()).lower()
            d['name_to_id'][cleaned_name] = item_id
            d['id_to_name'][item_id] = cleaned_name

        with open(data_directory+"/"+data_file_name, 'w') as fp:
            json.dump(d, fp, sort_keys=True, indent=4)

        return d
    else:
        print('Getting cached rune dictionary...')
        with open(data_directory+"/"+data_file_name, 'r') as fp:
            d = json.load(fp)
        return d

RUNE_DICTIONARY = get_rune_dict()