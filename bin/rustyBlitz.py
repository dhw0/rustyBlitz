import sys
import os
import pathlib
curr_dir_path = pathlib.Path(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(str(curr_dir_path.parent)+"/rustyBlitz")
from rune_selector import RuneSelector
from websocket_driver import websocket_runner
from driver import manual_rune_select, fully_manual_rune_select
import utils
import argparse
import json

# find lockfile location either automatically or manually
def initialize_league_location():
    # attempt to automatically find the league process, else just prompt the user to input the path manually and set the settings file
    # might only work if its run on WSL
    auto_find_league_process = str(utils.find_process_with_name_bash("LeagueClientUx.exe")).strip()
    if auto_find_league_process != "":
        return (utils.get_lockfile_data(auto_find_league_process+"/lockfile"))
    else:
        settings_file_loc = "settings.json"
        if not pathlib.Path(settings_file_loc).is_file():
            print("Input the install location of your League of Legends Instance.")
            print("This can be found by going to task manager --> League of legends --> dropdown --> right click --> properties --> location\n")
            league_path = input("Input your League path here -->\t")
            data = {'league_path':league_path.strip()}
            with open(settings_file_loc, 'w') as fp:
                json.dump(data, fp, sort_keys=True, indent=4)
                print("\nSettings file did not exist before, creating new settings file...")
                print("You can change the path of your League directory at this file: {}".format(str(curr_dir_path.parent)+"/bin/"+settings_file_loc))
            lockfile_data = (utils.get_lockfile_data(league_path+"/lockfile"))
        else:
            print('Settings file exists, loading in data from lockfile...')
            with open(settings_file_loc, 'r') as fp:
                data = json.load(fp)
            lockfile_data = (utils.get_lockfile_data(data['league_path'].strip().rstrip("/")+"/lockfile"))
        return lockfile_data


# completely automated rune selection
# in a draft mode, select runes based on position in champ select
def automatedRuneSelection():
    lockfile_data = initialize_league_location()
    websocket_runner(*lockfile_data)


# manual rune selection to override automatic selection
# Select the best runes from OPGG for champ in role
def manualRuneSelection():
    lockfile_data = initialize_league_location()
    parser = argparse.ArgumentParser()
    parser.add_argument("champion", help="The champion you are currently playing")
    parser.add_argument("-r", "--role", choices=["mid", "bot", "jungle", "top", "support"],
                        help="Optionally specify a role you want to play, if you don't want the selector to automatically select a role for you.")
    args = parser.parse_args()
    
    fully_manual_rune_select(lockfile_data, args.champion.lower(), role=args.role, no_confirm=True)
    


if __name__ == "__main__":
    manualRuneSelection()