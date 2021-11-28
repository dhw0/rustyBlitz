import json
import requests
from subprocess import check_output
import pathlib
import sys
import os
import datetime
import time

def write_dict_to_file(d, path):
    with open(path, 'w') as fp:
        json.dump(d, fp, sort_keys=True, indent=4)

def read_json_file(path):
    with open(path, 'r') as fp:
        d = json.load(fp)
    return d

def strip_punctuation(s):
    return ''.join(e for e in s if e.isalnum())

def get_next_patch_date(d, weekday):
    # https://stackoverflow.com/questions/6558535/find-the-date-for-the-first-monday-after-a-given-date

    days_ahead = weekday - d.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)

def find_process_with_name_bash(process_name):
    try:
        out = check_output(["wmic.exe", "process", "where", "caption=\"{}\"".format(process_name), "get", "executablepath"]).decode(sys.stdout.encoding)
        raw_windows_path = out.strip().split("\n")[1].strip()
        posix_path = check_output(["wslpath", "-a", raw_windows_path]).decode(sys.stdout.encoding)
        root_league_dir = pathlib.Path(posix_path.strip()).parent
        return root_league_dir
    except:
        return ""

def get_lockfile_data(lockfile_path):
    with open(lockfile_path, 'r') as f:
        data = f.readline().strip().split(':')
        # port, password, scheme
        return data[2], data[3], data[4]