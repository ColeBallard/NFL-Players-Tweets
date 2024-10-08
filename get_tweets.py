from player_handle_scraper import PlayerHandleScraper

if __name__ == '__main__':
    scraper = PlayerHandleScraper()
    print(scraper.saveHtmlToFile(url="https://www.pro-football-reference.com/players/A/AdamMi21.htm", filename="mike-adams.txt"))
    scraper.checkAndRefreshData()