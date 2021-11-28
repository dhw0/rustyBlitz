import sys
import os
import pathlib
import argparse
import json
from utils import get_lockfile_data, find_process_with_name_bash
from rune_selector import RuneSelector
import config

# manual loading of path from settings json file
def load_settings_from_file():
    curr_dir_path = pathlib.Path(os.path.dirname(os.path.abspath(__file__)))
    data_directory = str(curr_dir_path) + "/data"
    settings_file_loc = data_directory+"/settings.json"
    if not pathlib.Path(settings_file_loc).is_file():
        print("[CLI]:\t Input the install location of your League of Legends Instance.")
        print("[CLI]:\t This can be found by going to task manager --> League of legends --> dropdown --> right click --> properties --> location\n")
        league_path = input("Input your League path here -->\t")
        data = {'league_path':league_path.strip()}
        with open(settings_file_loc, 'w') as fp:
            json.dump(data, fp, sort_keys=True, indent=4)
            print("[CLI]:\t\t Settings file did not exist before, creating new settings file...")
            print("[CLI]:\t\t You can change the path of your League directory at this file: {}".format(settings_file_loc))
        lockfile_data = (get_lockfile_data(league_path+"/lockfile"))
    else:
        print('[CLI]:\t Settings file exists, loading in data from lockfile...')
        with open(settings_file_loc, 'r') as fp:
            data = json.load(fp)
        lockfile_data = (get_lockfile_data(data['league_path'].strip().rstrip("/")+"/lockfile"))
    return lockfile_data

# find lockfile location either automatically or manually
def initialize_league_location(process_scanning=False):
    # attempt to automatically find the league process, else just prompt the user to input the path manually and set the settings file
    # might only work if its run on WSL
    if process_scanning:
        print("[CLI]:\t Scanning process list to find running league instance...")
        auto_find_league_process = str(find_process_with_name_bash("LeagueClientUx.exe")).strip()
        if auto_find_league_process != "":
            print('[CLI]:\t\t Found process successfully')
            return (get_lockfile_data(auto_find_league_process+"/lockfile"))
        else:
            print("[CLI]:\t\t Failed to find a running league instance via process scanning, loading from settings file instead")
            return load_settings_from_file()
    else:
        return load_settings_from_file()


def runeSelectionRunner():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--champion", help="The champion you are currently playing")
    parser.add_argument("-r", "--role", choices=["mid", "bot", "jungle", "top", "support", "aram"],
                        help="Specify a role you want to play.")
    parser.add_argument("-s", "--scan", type=bool, help="Whether or not to scan process list", default=True)
    parser.add_argument("-d", "--dryrun", type=bool, help="Dry run the command (don't send a request to the client)", default=False)
    args = parser.parse_args()
    
    champ = args.champion
    role = args.role
    should_scan = args.scan
    dry_run = args.dryrun
    print("[CLI]:\t champ:", champ)
    print("[CLI]:\t role:", role)
    print("[CLI]:\t dry run mode:", dry_run)
    
    lockfile_data = initialize_league_location(args.scan)

    rs = RuneSelector(lockfile_data)

    resp = rs.populate_runes(champ, role, dry_run)

    config.RUNE_CACHE._write_to_disk()

if __name__ == "__main__":
    runeSelectionRunner()