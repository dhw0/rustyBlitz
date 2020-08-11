import requests
from requests.auth import HTTPBasicAuth
from scraper import OPGGScraper
import utils

from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# Manages the actual posting/getting of optimal rune data to league
class RuneSelector():
    def __init__(self, lockfile_path):
        self.port, self.password, self.scheme = utils.get_lockfile_data(lockfile_path)
        self.base_url = "{}://127.0.0.1:{}".format(self.scheme, str(self.port))
        self.auth_header = HTTPBasicAuth('riot', self.password)

    def get_current_rune_page_data(self):
        # endpoint to edit rune pages: /lol-perks/v1/pages/{id}
        formed_url = (self.base_url+"{}").format("/lol-perks/v1/currentpage")
        r = requests.get(formed_url, verify=False, auth=self.auth_header)
        return r.json()

    def post_rune_page_data(self, post_data, page_id):
        #formed_url = (self.base_url+"{}").format("/lol-perks/v1/pages/{}".format(str(page_id)))
        formed_url = (self.base_url+"{}").format("/lol-perks/v1/pages/{}".format(str(page_id)))
        r = requests.put(formed_url, verify=False, auth=self.auth_header, json=post_data)
        return r

    # best runes is a dictionary of the following type:
    # {"primary_type":0, "secondary_type":0, "primary": [], "secondary":[], "fragment":[]}
    # potentially cache champ, role, best runes?
    def form_request(self, champ, role, best_runes):
        page_id = self.get_current_rune_page_data()["id"]
        data = {}
        data["name"] = "AUTO: {} {}".format(champ,role)
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
