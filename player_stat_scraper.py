import string
import requests
from bs4 import BeautifulSoup

from player_scraper import PlayerScraper
import utilities as u

class PlayerStatScraper(PlayerScraper):
    def __init__(self, config_file="config.yaml", data_folder="data"):
        super().__init__(
            scraper_type='PLAYER_STAT', 
            config_file=config_file, 
            data_folder=data_folder, 
            refreshFunc=self.getNflPlayerStats
        )

        self.HEADERS = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                        ' Chrome/70.0.3538.77 Safari/537.36'
        }

        # 2006 is the year twitter was founded
        self.EARLIEST_YEAR = 2006

    def getNflPlayerStats(self):
        player_handles = self.csvToTable('PLAYER_HANDLE')
        data = {
            "headers": [],
            "data": []
        }

        page_num = 1

        for player_last_name_initial in string.ascii_uppercase:
            while True:
                player_list_soup = None

                try:
                    player_list_soup = self._getNflPlayerListSoup(
                        page_num=page_num,
                        player_last_name_initial=player_last_name_initial
                    )
                except Exception as e:
                    print(e)
                    continue

                if player_list_soup is None:
                    break

                for row in player_list_soup.find('tbody').find_all('tr'):
                    row_cells = row.find_all('td')

                    if u.strIncludesSeasonAfterYear(season_string=row_cells[3].text.strip(), year=self.EARLIEST_YEAR):
                        player_name = u.rearrangePlayerName(row_cells[0].find('a').text.strip())

                        if u.isStringInColumn(
                            table=player_handles, 
                            column_name='player_name', 
                            search_string=player_name
                        ):
                            player_url = 'https://www.footballdb.com' + row_cells[0].find('a')['href']
                            player_gamelog_years = self._getNflPlayerGamelogYears(player_url=player_url)

                            for player_year in player_gamelog_years:
                                player_stats_url = player_url + '/gamelogs/' + str(player_year)

                                try:
                                    self._extractNflPlayerStats(
                                        player_stats_url=player_stats_url,
                                        player_name=player_name,
                                        data=data
                                    )
                                except Exception as e:
                                    print(e)
                                    continue
                    else:
                        continue

                page_num += 1

        return data

    def _extractNflPlayerStats(self, player_stats_url, player_name, data):
        def _parseHeaderRow(th_elements):
            headers = []
            for th in th_elements:
                colspan = int(th.get('colspan', 1))
                text = th.get_text(strip=True)
                headers.extend([text] * colspan)
            return headers

        def _parseDataRow(td_elements):
            data_cells = []
            for td in td_elements:
                colspan = int(td.get('colspan', 1))
                nostatmsg = td.find('div', class_='nostatmsg')
                text = '' if nostatmsg else td.get_text(strip=True)
                data_cells.extend([text] * colspan)
            return data_cells
        
        response = requests.get(player_stats_url, headers=self.HEADERS)

        if response.status_code != 200:
            raise Exception(f"Failed to retrieve the webpage {player_stats_url}.\n{response.status_code}\n{response.headers}")

        player_stats_soup = BeautifulSoup(response.content, 'html.parser')

        tables = player_stats_soup.find_all('table', class_='statistics scrollable', attrs={'data-fixed-columns': '1'})

        for table in tables:
            # Extract headers
            thead = table.find('thead')
            header_rows = thead.find_all('tr')
            
            # Parse super-columns (first header row)
            super_headers = []
            if header_rows:
                first_header = header_rows[0]
                super_headers = _parseHeaderRow(first_header.find_all('th'))

            # Parse actual column names (second header row)
            column_headers = []
            if len(header_rows) > 1:
                second_header = header_rows[1]
                column_headers = _parseHeaderRow(second_header.find_all('th'))
            
            # Build full headers with prefixes
            headers = []
            for idx, col_name in enumerate(column_headers):
                super_col = super_headers[idx] if idx < len(super_headers) else ''
                # if col_name in ['Date', 'Team', 'Opp', 'Lg', 'Res']:
                #     header = col_name
                # else:
                header = f"{super_col}_{col_name}" if super_col else col_name
                headers.append(header)
            
            # Process data rows
            tbody = table.find('tbody')
            for tr in tbody.find_all('tr'):
                # Skip 'TOTALS' rows
                if 'header' in tr.get('class', []) and 'row_playerstats' in tr.get('class', []):
                    continue
                
                row_data = {}
                td_elements = tr.find_all('td')
                data_cells = _parseDataRow(td_elements)
                
                if len(data_cells) != len(headers):
                    continue  # Skip rows where data doesn't match headers
                
                for key, value in zip(headers, data_cells):
                    row_data[key] = value

                row_data['Player_Name'] = player_name
                
                data['data'].append(row_data)
                data['headers'] = list(set(data['headers']).union(row_data.keys()))

    def _getNflPlayerListSoup(self, page_num, player_last_name_initial):
        player_list_url = f'https://www.footballdb.com/players/players.html?page={page_num}&letter={player_last_name_initial}'

        response = requests.get(player_list_url, headers=self.HEADERS)

        if response.status_code != 200:
            raise Exception(f"Failed to retrieve the webpage {player_list_url}.\n{response.status_code}\n{response.headers}")

        player_list_soup = BeautifulSoup(response.content, 'html.parser')

        if len(player_list_soup.find('tbody').find_all('tr')) == 0:
            print(f'Finished extracting player data for last name initial {player_last_name_initial}.')
            return None
        
        return player_list_soup
    
    def _getNflPlayerGamelogYears(self, player_url):
        player_gamelog_url = player_url + '/gamelogs'

        response = requests.get(player_gamelog_url, headers=self.HEADERS)

        if response.status_code != 200:
            print(f"Failed to retrieve the webpage {player_gamelog_url}.\n{response.status_code}\n{response.headers}")
            return

        player_gamelog_soup = BeautifulSoup(response.content, 'html.parser')

        if len(player_gamelog_soup.find_all(class_='report-form-right')) == 0:
            print(f'No gamelog years found at {player_gamelog_url}.')
            return
        
        gamelog_years = []
        
        # Extract the latest year as it doesn't seem to be included in the dropdown list
        try:
            gamelog_years.append(
                str(u.extractYear(
                    player_gamelog_soup.find_all(class_='report-form-right')[0].find(id='dropdownGamelogsYear').text.strip()
                ))
            )
        except Exception as e:
            print(f'Unable to get latest year from {player_gamelog_url}.')

        for list_item in player_gamelog_soup.find_all(class_='report-form-right')[0].find(class_='dropdown-menu').find_all('li'):
            gamelog_year = str(list_item.find('a').text.strip())

            if int(gamelog_year) >= self.EARLIEST_YEAR:
                gamelog_years.append(gamelog_year)

        return list(set(gamelog_years))
    