import os
import csv
import yaml
import requests
from bs4 import BeautifulSoup

class PlayerHandleScraper:
    def __init__(self, config_file="config.yaml", csv_file="player_handle_map.csv"):
        self.config_file = config_file
        self.csv_file = csv_file
        self.config = self.loadOrCreateConfig()

    def loadOrCreateConfig(self):
        if not os.path.exists(self.config_file):
            default_config = {
                'refresh_player_handles': False,
                'csv_file': self.csv_file
            }
            with open(self.config_file, 'w') as file:
                yaml.dump(default_config, file)
            return default_config
        else:
            with open(self.config_file, 'r') as file:
                return yaml.safe_load(file)

    def updateConfig(self, key, value):
        self.config[key] = value
        with open(self.config_file, 'w') as file:
            yaml.dump(self.config, file)

    def getNflPlayersAndHandles(self, url="https://www.pro-football-reference.com/friv/nfl-player-twitter.htm"):
        response = requests.get(url)
        if response.status_code != 200:
            print("Failed to retrieve the webpage")
            return []

        soup = BeautifulSoup(response.content, 'html.parser')
        player_info = []
        for player in soup.find_all('p'):
            player_name_link = player.find('a', href=lambda href: href and '/players/' in href)
            twitter_link = player.find('a', href=lambda href: href and 'twitter.com' in href)

            if player_name_link and twitter_link:
                player_name = player_name_link.text
                player_profile = 'https://www.pro-football-reference.com' + player_name_link['href']
                twitter_username = twitter_link.text
                twitter_profile = twitter_link['href']
                
                player_info.append({
                    'player_name': player_name,
                    'player_profile': player_profile,
                    'twitter_username': twitter_username,
                    'twitter_profile': twitter_profile
                })

        return player_info
    
    def saveNflPlayersToCsv(self, players_data, filename=None):
        if filename is None:
            filename = self.config['csv_file']
        
        headers = ['player_name', 'profile_link', 'twitter_username', 'twitter_profile']
        
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()
            
            for player in players_data:
                writer.writerow({
                    'player_name': player['player_name'],
                    'profile_link': player['player_profile'],
                    'twitter_username': player['twitter_username'],
                    'twitter_profile': player['twitter_profile']
                })

        print(f"Data saved to {filename}")
    
    def checkAndRefreshData(self):
        if not os.path.exists(self.csv_file) or self.config.get('refresh_player_handles', False):
            print("Refreshing player data...")
            nfl_players_and_handles = self.getNflPlayersAndHandles()
            self.saveNflPlayersToCsv(nfl_players_and_handles)
            self.updateConfig('refresh_player_handles', False)
        else:
            print(f"CSV file {self.csv_file} already exists and refresh_player_handles is set to False. No refresh needed.")
    
    def printHtmlFromUrl(self, url="https://www.pro-football-reference.com/friv/nfl-player-twitter.htm"):
        try:
            response = requests.get(url)
            response.raise_for_status()
            print(response.text)
        
        except requests.exceptions.RequestException as error:
            print(f"Error fetching the webpage: {error}")

    def saveHtmlToFile(self, url="https://www.pro-football-reference.com/friv/nfl-player-twitter.htm", filename="nfl_player_ats.txt"):
        try:
            response = requests.get(url)
            response.raise_for_status()

            with open(filename, 'w', encoding='utf-8') as file:
                file.write(response.text)
            
            print(f"HTML content successfully saved to {filename}")

        except requests.exceptions.RequestException as error:
            print(f"Error fetching the webpage: {error}")