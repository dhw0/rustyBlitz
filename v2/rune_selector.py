from client_interface import ClientInterface
from scraper import OPGGScraper
import config

class RuneSelector():
    def __init__(self, lockfile_data):
        # support multiple scrapers in the future
        self.scraper = OPGGScraper()
        self.client = ClientInterface(*lockfile_data)

    def populate_runes(self, champ, role, dry_run=False):
        rune_data = self.scraper.get_best_runes(champ, role)
        resp = None
        if not dry_run:
            resp = self.client.post_rune_page_data(rune_data)
            assert resp.status_code == 201
        return resp