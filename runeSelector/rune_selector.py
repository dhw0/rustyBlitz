import requests
from requests.auth import HTTPBasicAuth
import time
import pprint
from scraper import OPGGScraper
pp = pprint.PrettyPrinter(depth=6)
import argparse
import sys
import utils

# Suppress only the single warning from urllib3 needed.
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


class RuneSelector():
    def __init__(self, lockfile_path):
        self.port, self.password, self.scheme = utils.get_lockfile_data(lockfile_path)
        self.base_url = "{}://127.0.0.1:{}".format(self.scheme, str(self.port))
        self.auth_header = HTTPBasicAuth('riot', self.password)

        #print("Listening on port {}, with password: {}".format(self.base_url, self.password))

    def get_current_rune_page_data(self):
        # endpoint to edit rune pages: /lol-perks/v1/pages/{id}
        formed_url = (self.base_url+"{}").format("/lol-perks/v1/currentpage")
        r = requests.get(formed_url, verify=False, auth=self.auth_header)
        return r.json()

    def post_rune_page_data(self, post_data, page_id):
        #formed_url = (self.base_url+"{}").format("/lol-perks/v1/pages/{}".format(str(page_id)))
        formed_url = (self.base_url+"{}").format("/lol-perks/v1/pages/{}".format(str(page_id)))
        pp.pprint(post_data)
        r = requests.put(formed_url, verify=False, auth=self.auth_header, json=post_data)
        return r

    def form_request(self, champ):
        page_id = self.get_current_rune_page_data()["id"]
        scraper = OPGGScraper(champ)
        best_runes = scraper.get_best_runes()
        data = {}
        data["name"] = "AUTO: {} {}".format(champ,scraper.role)
        data["primaryStyleId"] = best_runes["primary_type"]
        data["subStyleId"] = best_runes["secondary_type"]
        all_perks = best_runes["primary"]
        all_perks.extend(best_runes["secondary"])
        all_perks.extend(best_runes["fragment"])
        data["selectedPerkIds"] = all_perks
        data["current"] = True
        data["isActive"] = True
        #data["id"] = page_id
        return data, page_id

    def get_champion(self):
        formed_url = (self.base_url+"{}").format("/lol-champ-select/v1/current-champion")
        r = requests.get(formed_url, verify=False, auth=self.auth_header)
        return r.json()


def rune_selector_runner():
    rs = RuneSelector("/mnt/g/games/LeagueOfLegends/League of Legends/lockfile")
    print("current rune page:")
    resp = rs.get_current_rune_page_data()
    pp.pprint(resp)

    if len(sys.argv) < 3:
        print("python file.py <CHAMP>")
    else:
        champ = sys.argv[1].strip()
        role = sys.argv[2].strip()
        print("New rune page for {} in role {}".format(champ, role))
        agree = input("Make rune page changes to this rune page?\t")
        if agree.strip().lower() == "y" or agree.strip().lower() == "yes":
            print("Setting up new rune page...")
            post_data, page_id = rs.form_request(champ, role)
            r = rs.post_rune_page_data(post_data, page_id)
            print(r.status_code)

            print("New rune page set:")
            resp = rs.get_current_rune_page_data()
            pp.pprint(resp)
        else:
            print("Rune page not set.")

def rune_selector_runner_automated():
    rs = RuneSelector("/mnt/g/games/LeagueOfLegends/League of Legends/lockfile")
    print("current rune page:")
    resp = rs.get_current_rune_page_data()
    pp.pprint(resp)

    champ = sys.argv[1].strip()
    print("New rune page for {}".format(champ))
    post_data, page_id = rs.form_request(champ)
    pp.pprint(post_data)


def test_rune_selector():
    rs = RuneSelector("/mnt/g/games/LeagueOfLegends/League of Legends/lockfile")
    test = rs.get_champion()
    print(test)

def test_scraper(champ):
    scraper = OPGGScraper(champ)
    print(scraper.get_most_played_positions())

if __name__ == '__main__':
    #test_scraper("sett")
    #rune_selector_runner()
    rune_selector_runner_automated()