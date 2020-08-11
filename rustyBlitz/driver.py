from rune_selector import RuneSelector
import pprint
pp = pprint.PrettyPrinter(depth=6)
import sys
from scraper import OPGGScraper

# not automated version that takes in champ/role arguments
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

# fully automated version that takes in nothing (i.e gets champ based off websocket event)
def rune_selector_runner_automated():
    rs = RuneSelector("/mnt/g/games/LeagueOfLegends/League of Legends/lockfile")
    print("current rune page:")
    resp = rs.get_current_rune_page_data()
    pp.pprint(resp)

    champ = sys.argv[1].strip()
    print("New rune page for {}".format(champ))

    scraper = OPGGScraper(champ)
    print("Automatically chose role {} based on popularity: ".format(scraper.role))
    best_runes = scraper.get_best_runes()

    post_data, page_id = rs.form_request(champ, scraper.role, best_runes)
    pp.pprint(post_data)
    print()
    available_roles = [x[0] for x in scraper.get_most_played_positions()]
    new_role = input("The following roles are available: {}. Pick a new role?\t".format(",".join(available_roles)))
    if new_role.strip().lower() in available_roles:
        print("Getting new best runes...")
        scraper.role = new_role.strip().lower()
        best_runes = scraper.get_best_runes()


    post_data, page_id = rs.form_request(champ, scraper.role, best_runes)
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