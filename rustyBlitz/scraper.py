from bs4 import BeautifulSoup
import requests

opgg_base_url = "https://www.op.gg/champion/{}/statistics/{}"
raw_opgg_base_url = "https://www.op.gg/{}"

def clean_role(role):
    if role.lower().strip() == "middle":
        return "mid"
    elif role.lower().strip() == "bottom":
        return "bot"
    if role.lower().strip() == "jungle":
        return "jungle"
    elif role.lower().strip() == "top":
        return "top"
    elif role.lower().strip() == "support":
        return "support"
    else:
        return None

# OPGG scraper is an object that handles the scraping of runes from opgg
# on init, it finds the most played role for a champ and automatically assigns runes for that particular role (can be overridden)
class OPGGScraper():
    def __init__(self):
        pass
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
    def extract_runes(self, runes, raw_rune_data):
        rune_data_primary = raw_rune_data[1:5]
        rune_data_secondary = raw_rune_data[6:]
        for rune_row in rune_data_primary:
            rune_row_soup = BeautifulSoup(str(rune_row), 'html.parser')
            rune_row_data = rune_row_soup.select("div[class*=active]")
            if(len(rune_row_data) > 0):
                rune_image_link = BeautifulSoup(str(rune_row_data), 'html.parser').find_all("img")
                rune_id = self.convert_image_link_to_rune_id("/lol/perk/", rune_image_link[0]["src"])
                runes["primary"].append(rune_id)

        for rune_row in rune_data_secondary:
            rune_row_soup = BeautifulSoup(str(rune_row), 'html.parser')
            rune_row_data = rune_row_soup.select("div[class*=active]")
            if(len(rune_row_data) > 0):
                rune_image_link = BeautifulSoup(str(rune_row_data), 'html.parser').find_all("img")
                rune_id = self.convert_image_link_to_rune_id("/lol/perk/", rune_image_link[0]["src"])
                runes["secondary"].append(rune_id)
        

    def extract_primary_and_secondary_runes(self, runes, raw_rune_data):
        primary_rune = raw_rune_data[0]
        secondary_rune = raw_rune_data[5]

        for i, curr_rune in zip(range(2), [primary_rune, secondary_rune]):
            curr_rune_soup = BeautifulSoup(str(curr_rune), 'html.parser')
            rune_image_link = curr_rune_soup.find_all("img")
            rune_id = self.convert_image_link_to_rune_id("/lol/perkStyle/", rune_image_link[0]["src"])
            if i == 0:
                runes["primary_type"] = rune_id
            else:
                runes["secondary_type"] = rune_id
        
    def extract_fragment_data(self, runes, raw_fragment_data):
        for fragment in raw_fragment_data:
            curr_frag_soup = BeautifulSoup(str(fragment), 'html.parser')
            frag_image_link = curr_frag_soup.find_all(class_="active tip")
            rune_id = self.convert_image_link_to_rune_id("/lol/perkShard/", frag_image_link[0]["src"])
            runes["fragment"].append(rune_id)

    def populate_runes(self, runes, champ, role):

        page = requests.get(opgg_base_url.format(champ, role), allow_redirects=False)
        try:
            page_soup = BeautifulSoup(page.text, 'html.parser')
            best_rune_data = page_soup.find_all(class_="perk-page-wrap")[0]

            rune_soup = BeautifulSoup(str(best_rune_data), 'html.parser')
            raw_rune_data = rune_soup.find_all(class_="perk-page__row") # main runepage data
            raw_fragment_data = rune_soup.find_all(class_="fragment__row") # fragment rune page data

            self.extract_primary_and_secondary_runes(runes, raw_rune_data)
            self.extract_runes(runes, raw_rune_data)
            self.extract_fragment_data(runes, raw_fragment_data)
            return True
        except Exception as e:
            print(e)
            return False

    def get_most_played_positions(self, champ):
        roles = [] # list of tuples (role, link path, winrate)

        page = requests.get(raw_opgg_base_url.format("champion/{}/statistics/".format(champ)), allow_redirects=False)
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
            print(e)
            pass
        return roles
    
    def get_optimal_role(self, champ):
        return self.get_most_played_positions(champ)[0][0]

    # main driver, gets best runes for champ/role
    def get_best_runes(self, champ, role_override=None):
        if(role_override == None):
            role = self.get_optimal_role(champ)
        else:
            role = role_override
        runes = {"name": "AUTO: {} {}".format(champ, role), "primary_type":0, "secondary_type":0, "primary": [], "secondary":[], "fragment":[]}
        if not self.populate_runes(runes, champ, role):
            return None
        return runes