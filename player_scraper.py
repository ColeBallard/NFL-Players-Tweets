import os
import csv
import yaml

class PlayerScraper:
    def __init__(self, scraper_type='', config_file="config.yaml", data_folder="data", refreshFunc=None):
        self.SCRAPER_TYPES = {
            'PLAYER_HANDLE': 'player_handle',
            'PLAYER_STAT': 'player_stat'
        }

        self.scraper_type = self.SCRAPER_TYPES.get(scraper_type, scraper_type)
        self.config_file = config_file
        self.data_folder = data_folder

        self.csv_file = f'{self.scraper_type}.csv'
        self.csv_file_path = os.path.join(data_folder, self.csv_file)

        self.refresh_var = f'refresh_{self.scraper_type}'
        self.csv_file_var = f'{self.scraper_type}_csv_file'

        self.refreshFunc = refreshFunc

        self.config = self.loadOrCreateConfig()
        
        # Ensure the data directory exists
        os.makedirs(self.data_folder, exist_ok=True)

    def loadOrCreateConfig(self):
        default_config = {
            self.refresh_var: False,
            self.csv_file_var: self.csv_file
        }

        config = default_config

        if not os.path.exists(self.config_file):
            with open(self.config_file, 'w') as file:
                yaml.dump(default_config, file)
        else:
            with open(self.config_file, 'r') as file:
                config = yaml.safe_load(file) or {}
            
            # Check for missing keys and add them if necessary
            updated = False
            for key, value in default_config.items():
                if key not in config:
                    config[key] = value
                    updated = True
            
            # Write back to the config file if updates were made
            if updated:
                with open(self.config_file, 'w') as file:
                    yaml.dump(config, file)

        return config

    def updateConfig(self, key, value):
        self.config[key] = value
        with open(self.config_file, 'w') as file:
            yaml.dump(self.config, file)
    
    def checkAndRefreshData(self):
        if not os.path.exists(self.csv_file_path) or self.config.get(self.refresh_var, False):
            print(f"Refreshing {self.scraper_type} data...")
            refreshed_data = self.refreshFunc()
            self.tableToCsv(refreshed_data)
            self.updateConfig(self.refresh_var, False)
        else:
            print(f"CSV file {self.csv_file_path} already exists and refresh_player_handles is set to False. No refresh needed.")

    def tableToCsv(self, table_data):
        headers = table_data['headers']
        data = table_data['data']

        with open(self.csv_file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data)

        print(f"Data saved to {self.csv_file_path}")

    def csvToTable(self, data_type):
        data_type = self.SCRAPER_TYPES.get(data_type, data_type)

        csv_file = f'{data_type}.csv'
        csv_file_path = os.path.join(self.data_folder, csv_file)

        with open(csv_file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            # Extract header (fieldnames from the CSV file)
            headers = reader.fieldnames
            # Convert the CSV into a list of dictionaries for the rows
            data = list(reader)

            return {
                "headers": headers,  # List of column names
                "data": data        # List of rows, each row is a dictionary
            }