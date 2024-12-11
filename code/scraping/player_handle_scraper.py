import requests
from bs4 import BeautifulSoup

from player_scraper import PlayerScraper
import utilities as u

class PlayerHandleScraper(PlayerScraper):
    def __init__(self):
        super().__init__(
            scraper_type='PLAYER_HANDLE',
            refreshFunc=self.getNflPlayersAndHandles
        )

    def getNflPlayersAndHandles(self, url="https://www.pro-football-reference.com/friv/nfl-player-twitter.htm"):
        response = requests.get(url)
        if response.status_code != 200:
            print("Failed to retrieve the webpage")
            return []

        player_handle_soup = BeautifulSoup(response.content, 'html.parser')
        players_data = []
        headers = ['player_id', 'player_name', 'player_profile', 'twitter_username', 'twitter_profile']
        for player in player_handle_soup.find_all('p'):
            player_name_link = player.find('a', href=lambda href: href and '/players/' in href)
            twitter_link = player.find('a', href=lambda href: href and 'twitter.com' in href)

            if player_name_link and twitter_link:
                player_id = u.extractPlayerId(player_name_link['href'])
                player_name = player_name_link.text
                player_profile = 'https://www.pro-football-reference.com' + player_name_link['href']
                twitter_username = twitter_link.text
                twitter_profile = twitter_link['href']
                
                players_data.append({
                    'player_id': player_id,
                    'player_name': player_name,
                    'player_profile': player_profile,
                    'twitter_username': twitter_username,
                    'twitter_profile': twitter_profile
                })

        return {'headers': headers, 'data': players_data}