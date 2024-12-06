from player_handle_scraper import PlayerHandleScraper
from player_stat_scraper import PlayerStatScraper
from player_tweet_scraper import PlayerTweetScraper

if __name__ == '__main__':
    player_handle_scraper = PlayerHandleScraper()
    player_handle_scraper.checkAndRefreshData()

    player_stat_scraper = PlayerStatScraper()
    player_stat_scraper.checkAndRefreshData()

    player_tweet_scraper = PlayerTweetScraper()
    player_tweet_scraper.checkAndRefreshData()