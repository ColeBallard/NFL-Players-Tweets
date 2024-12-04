from player_handle_scraper import PlayerHandleScraper
from player_stat_scraper import PlayerStatScraper

if __name__ == '__main__':
    player_handle_scraper = PlayerHandleScraper()
    player_handle_scraper.checkAndRefreshData()

    player_stat_scraper = PlayerStatScraper()
    player_stat_scraper.checkAndRefreshData()