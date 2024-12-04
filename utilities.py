import re

def strIncludesSeasonAfterYear(season_string, year):
    # Extract all year ranges and single years using regex
    year_matches = re.findall(r'(\d{4})(?:-(\d{4}))?', season_string)
    
    for start_year, end_year in year_matches:
        start_year = int(start_year)
        end_year = int(end_year) if end_year else start_year
        
        # Check if any year in the range is 2006 or later
        if start_year <= year <= end_year or start_year >= year:
            return True
    
    return False

def rearrangePlayerName(s):
    if ',' in s:
        # Split the string at the comma
        before_comma, after_comma = s.split(',', 1)
        # Rearrange to put the part after the comma at the front
        return f"{after_comma.strip()} {before_comma.strip()}"
    return s  # Return the original string if no comma is found

def isStringInColumn(table, column_name, search_string):
    data = table["data"]

    # Check if the string exists in the specified column
    for row in data:
        if row.get(column_name) and search_string == row[column_name]:
            return True
        
    return False

def extractYear(season_string):
    # Use a regular expression to extract the year
    match = re.search(r'\b\d{4}\b', season_string)
    if match:
        return int(match.group())
    else:
        raise ValueError("No valid year found in the input string.")
    
def extractPlayerId(s):
    # Split the string by slashes and pick the last part
    last_part = s.split('/')[-1]
    # Remove the '.htm' extension
    player_id = last_part.replace('.htm', '')

    return player_id