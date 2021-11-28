from bs4 import BeautifulSoup
import requests
import string
from utils import RUNE_DICTIONARY
import os

def clean_role(role):
    if(role is None):
        return "Auto Role"
    cleaned_role = role.lower().strip()
    if cleaned_role == "middle" or cleaned_role == "mid":
        return "mid"
    elif cleaned_role == "bottom" or cleaned_role== "bot":
        return "bot"
    if cleaned_role == "jungle" or cleaned_role == "jg" or cleaned_role == "jung":
        return "jungle"
    elif cleaned_role == "top":
        return "top"
    elif cleaned_role == "support" or cleaned_role == "supp" or cleaned_role == 'utility':
        return "support"
    else:
        return None

def list_runes(runes):
    print('Name', runes['name'])
    print('Main tree: ', RUNE_DICTIONARY['id_to_name'][str(runes['primary_type'])])
    for item in runes['primary']:
        print('\t',RUNE_DICTIONARY['id_to_name'][str(item)]['detailed_name'])
    print('Secondary tree: ', RUNE_DICTIONARY['id_to_name'][str(runes['secondary_type'])])
    for item in runes['secondary']:
        print('\t',RUNE_DICTIONARY['id_to_name'][str(item)]['detailed_name'])
    print('Fragments: ')
    for item in runes['fragment']:
        print('\t', RUNE_DICTIONARY['id_to_name'][str(item)]['detailed_name'])

# OPGG scraper is an object that handles the scraping of runes from opgg
# on init, it finds the most played role for a champ and automatically assigns runes for that particular role (can be overridden)
class OPGGScraper():
    def __init__(self):
        self.opgg_base_url = "https://www.op.gg/champion/{}/statistics/{}"
        self.raw_opgg_base_url = "https://www.op.gg/{}"
    # returns int rune id
    def convert_image_link_to_rune_id(self, prefix, image_link):
        idx = image_link.index(prefix)
        if(idx < 0):
            return 0
        png_idx = image_link.index(".png")
        if(png_idx < 0):
            return 0
        return int(image_link[idx+len(prefix):png_idx])

    # modifies rune datastructure in place
    def extract_runes(self, raw_rune_data):
        rune_data_primary = raw_rune_data[1:5]
        rune_data_secondary = raw_rune_data[6:10]

        primary_res = []
        secondary_res = []
        for rune_row in rune_data_primary:
            rune_row_soup = BeautifulSoup(str(rune_row), 'html.parser')
            rune_row_data = rune_row_soup.select("div[class*=active]")
            if(len(rune_row_data) > 0):
                rune_image_link = BeautifulSoup(str(rune_row_data), 'html.parser').find_all("img")
                rune_id = self.convert_image_link_to_rune_id("/lol/perk/", rune_image_link[0]["src"])
                #runes["primary"].append(rune_id)
                primary_res.append(rune_id)

        for rune_row in rune_data_secondary:
            rune_row_soup = BeautifulSoup(str(rune_row), 'html.parser')
            rune_row_data = rune_row_soup.select("div[class*=active]")
            if(len(rune_row_data) > 0):
                rune_image_link = BeautifulSoup(str(rune_row_data), 'html.parser').find_all("img")
                rune_id = self.convert_image_link_to_rune_id("/lol/perk/", rune_image_link[0]["src"])
                #runes["secondary"].append(rune_id)
                secondary_res.append(rune_id)

        return {
            "primary":primary_res,
            "secondary":secondary_res
        }

    def extract_primary_and_secondary_runes(self, raw_rune_data):
        primary_rune = raw_rune_data[0]
        secondary_rune = raw_rune_data[5]
        primary_type = -1
        secondary_type = -1

        for i, curr_rune in zip(range(2), [primary_rune, secondary_rune]):
            curr_rune_soup = BeautifulSoup(str(curr_rune), 'html.parser')
            rune_image_link = curr_rune_soup.find_all("img")
            rune_id = self.convert_image_link_to_rune_id("/lol/perkStyle/", rune_image_link[0]["src"])
            if i == 0:
                #runes["primary_type"] = rune_id
                primary_type = rune_id
            else:
                #runes["secondary_type"] = rune_id
                secondary_type = rune_id
        return {
            "primary_type": primary_type,
            "secondary_type":secondary_type
        }


    def extract_fragment_data(self, raw_fragment_data):
        fragment_res = []
        for fragment in raw_fragment_data[:3]:
            curr_frag_soup = BeautifulSoup(str(fragment), 'html.parser')
            frag_image_link = curr_frag_soup.find_all(class_="active tip")
            rune_id = self.convert_image_link_to_rune_id("/lol/perkShard/", frag_image_link[0]["src"])
            #runes["fragment"].append(rune_id)
            fragment_res.append(rune_id)
        return {
            "fragment":fragment_res
        }


    def populate_runes(self, champ, role):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',
        }
        page = requests.get(self.opgg_base_url.format(champ, role), headers=headers)
        print(self.opgg_base_url.format(champ, role))
        try:
            page_soup = BeautifulSoup(page.text, 'html.parser')
            best_rune_data = page_soup.find_all(class_="perk-page-wrap")#[0]

            rune_soup = BeautifulSoup(str(best_rune_data), 'html.parser')
            raw_rune_data = rune_soup.find_all(class_="perk-page__row") # main runepage data
            raw_fragment_data = rune_soup.find_all(class_="fragment__row") # fragment rune page data

            rune_types = self.extract_primary_and_secondary_runes(raw_rune_data)
            main_runes = self.extract_runes(raw_rune_data)
            fragment_runes = self.extract_fragment_data(raw_fragment_data)
            rune_set = {**rune_types, **main_runes, **fragment_runes}

            return {
                "rune_set":rune_set,
                "failed":None
            }
        except Exception as e:
            print('POPULATE_RUNES ERROR: ', e)
            return {
                "rune_set":{},
                "failed":str(e)
            }

    def get_most_played_positions(self, champ):
        roles = [] # list of tuples (role, link path, winrate)
        page = requests.get(self.raw_opgg_base_url.format("champion/{}/statistics/".format(champ)))
        try:
            page_soup = BeautifulSoup(page.text, 'html.parser')
            possible_roles = page_soup.select("li[class*=champion-stats-header__position]")

            for role in possible_roles:
                role_soup = BeautifulSoup(str(role), 'html.parser')
                role_link = role_soup.find_all("a")
                role_name = role_soup.find_all(class_="champion-stats-header__position__role")
                role_winrate = role_soup.find_all(class_="champion-stats-header__position__rate")

                role_item = (clean_role(role_name[0].text), role_link[0]['href'], role_winrate[0].text)
                roles.append(role_item)
        except Exception as e:
            print('GET_MOST_PLAYED_POSITIONS ERROR: ', e)
            pass
        return roles
    
    def get_optimal_role(self, champ):
        return self.get_most_played_positions(champ)[0][0]

    # main driver, gets best runes for champ/role
    def get_best_runes(self, raw_champ, role_override=None):
        champ = raw_champ.translate(str.maketrans('', '', string.punctuation)).lower().strip()
        if(role_override == None):
            role = clean_role(self.get_optimal_role(champ))
        else:
            role = clean_role(role_override)
        rune_candidates = self.populate_runes(champ, role)
        if(rune_candidates['failed'] is not None):
            return None, rune_candidates['failed']
        runes = rune_candidates["rune_set"]
        page_name = "OP.GG AUTO: {} {}".format(raw_champ, role)
        runes["name"] = page_name
        list_runes(runes)
        return runes, rune_candidates['failed']


# OPGG scraper is an object that handles the scraping of runes from opgg
# on init, it finds the most played role for a champ and automatically assigns runes for that particular role (can be overridden)
class UGGScraper():
    def __init__(self):
        self.base_url = "https://u.gg/lol/champions/{}/runes" # for default most played role
        self.base_url_role = "https://u.gg/lol/champions/{}/runes?role={}" # for a specific role


    def _rune_parser(self, raw_rune_text, prefix, suffix):
        lower_all_alnum = ''.join(e for e in raw_rune_text if e.isalnum()).lower() 
        end = -1 * len(suffix)
        if(end == 0):
            end = len(lower_all_alnum)
        start = len(prefix)
        if(prefix != "" and lower_all_alnum.find(prefix) == -1):
            return ""
        if(suffix != "" and lower_all_alnum.find(suffix) == -1):
            return ""
        rune_name = os.path.basename(lower_all_alnum)[start:end].strip()
        cleaned = ''.join(e for e in rune_name if e.isalnum()).lower()
        if(cleaned == "adaptiveforce"):
            return "adaptive"
        if(cleaned == "magicresist"):
            return "magicres"
        if(cleaned == "scalingcdr"):
            return "cdrscaling"
        return cleaned

    def get_rune_id(self, div, prefix="", suffix=""):
        rune_image_link = BeautifulSoup(str(div), 'html.parser').find_all("img")
        rune_url = rune_image_link[0]['src']
        rune_name = os.path.basename(rune_url)[len(prefix):-1*len(suffix)]

        cleaned_name_from_alt = self._rune_parser(rune_image_link[0]['alt'], prefix=prefix, suffix=suffix)
        try:
            rune_id = RUNE_DICTIONARY['name_to_id'][cleaned_name_from_alt]
            return rune_id
        except KeyError as e:
            print('Failed to parse: ', rune_image_link[0]['alt'])
            print('Got: ', cleaned_name_from_alt)
            return -1

    def get_runes_from_primary_tree(self, raw_rune_html):
        res = []
        primary_tree_soup = BeautifulSoup(str(raw_rune_html), 'html.parser')
        keystone = primary_tree_soup.find_all(class_="perk keystone perk-active")
        res.append(self.get_rune_id(keystone, prefix="thekeystone"))
        rest = primary_tree_soup.find_all(class_="perk perk-active")
        for rune in rest:
            res.append(self.get_rune_id(rune, prefix="therune"))
        style = primary_tree_soup.find_all(class_="perk-style-title")
        return {
            "primary_type":RUNE_DICTIONARY['name_to_id'][style[0].text.lower()],
            "primary":res
        }
    
    def get_fragments(self, raw_rune_html):
        res = []
        fragment_tree_soup = BeautifulSoup(str(raw_rune_html), 'html.parser')
        rest = fragment_tree_soup.find_all(class_="shard shard-active")
        for rune in rest:
            res.append(self.get_rune_id(rune, prefix="the", suffix="shard"))
        return {
            "fragment":res
        }

    def get_runes_from_secondary_tree(self, raw_rune_html):
        res = []
        secondary_tree_soup = BeautifulSoup(str(raw_rune_html), 'html.parser')
        rest = secondary_tree_soup.find_all(class_="perk perk-active")
        for rune in rest:
            res.append(self.get_rune_id(rune, prefix="therune"))
        style = secondary_tree_soup.find_all(class_="perk-style-title")
        return {
            "secondary_type":RUNE_DICTIONARY['name_to_id'][style[0].text.lower()],
            "secondary":res
        }

    # modifies rune datastructure in place
    def extract_runes(self, champ, role = None):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',
        }
        if(role is None):
            page = requests.get(self.base_url.format(champ), headers=headers)
        else:
            page = requests.get(self.base_url_role.format(champ, role), headers=headers)

        page_soup = BeautifulSoup(page.text, 'html.parser')
        primary_tree = page_soup.find_all(class_="rune-tree_v2 primary-tree")[0]
        secondary_tree = page_soup.find_all(class_="secondary-tree")[0]

        primary_rune_set = self.get_runes_from_primary_tree(primary_tree)
        secondary_rune_set = self.get_runes_from_secondary_tree(secondary_tree)
        fragment_rune_set = self.get_fragments(secondary_tree)

        rune_set = {**primary_rune_set, **secondary_rune_set, **fragment_rune_set}
        return {
            "rune_set":rune_set,
            "failed":None
        }

    # main driver, gets best runes for champ/role
    def get_best_runes(self, raw_champ, role_override=None):
        role = clean_role(role_override)
        champ = raw_champ.translate(str.maketrans('', '', string.punctuation)).lower().strip()
        rune_candidates = self.extract_runes(champ, role)
        if(rune_candidates['failed'] is not None):
            return None, rune_candidates['failed']
        runes = rune_candidates["rune_set"]
        runes["name"] = "U.GG AUTO: {} {}".format(raw_champ, role)
        list_runes(runes)
        return runes, rune_candidates['failed']