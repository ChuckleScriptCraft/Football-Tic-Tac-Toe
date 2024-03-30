# Packages
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import sys
from fuzzywuzzy import fuzz

# Collect headers for interacting with TM

sys.path.insert(1, '../secret/')

import headers

# Import lookup for tmarkt url
url_lookup = pd.read_csv('../data/url_lookup.csv', encoding='latin-1')


# Get player's clubs from fbref
def get_player_clubs_fbref(player_name) :
    
    """
    Get the clubs a football player has played for using data from FBref.com.

    Args:
        player_name (str): The name of the football player.

    Returns:
        set: A set of club names the player has played for according to FBref.com.
    """
    
    # Get URL based on player name
    url = f"https://fbref.com/en/search/search.fcgi?search={player_name.replace(' ', '+')}"
    
    # Send a GET request to the URL and parse the HTML content
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the specific element containing player stats
    specific_element = soup.find('div', {'id': 'div_stats_misc_dom_lg'})
    tables = specific_element.find_all('table')
    
    squad = []
    
    # Iterate over each table
    for table in tables:
        # Find all rows within the table
        rows = table.find_all('tr')
        
        # Iterate over each row
        for row in rows:
            # Find all columns within the row
            cols = row.find_all(['th', 'td'])
            squad.append(cols[2].get_text(strip=True))
            
    # Find the index of the first blank element
    index_of_blank = squad.index('') if '' in squad else len(squad)
    
    # Create a set of club names excluding the first two elements
    club_names = set(squad[2:index_of_blank])
    
    return(club_names)  


# Get player's clubs from transfermarkt

def get_player_clubs_tmarkt(player_name) :
    """
    Retrieve unique club names from a player's transfer history on Transfermarkt.

    Parameters:
        player_name (str): The name of the player.

    Returns:
        set: A set containing unique club names from the player's transfer history.
    """
    
    # Retrieve URL from the url_lookup DataFrame for the given player name
    # Convert player_name to title case for consistency 
    url = url_lookup[url_lookup['name'] == player_name.title()]['url']
    url = '\n'.join(url)
    
    ## Retrieve player ID from the URL
    player_id = url.split('/')[-1]
    
    # Call Transfermarkt API to get the player's transfer history
    response = requests.get(f'https://www.transfermarkt.co.uk/ceapi/transferHistory/list/{player_id}', headers=headers.headers)
    
    # Convert the response to JSON format
    transfer_data = response.json()
    
    # Extract unique club names from the player's transfer history
    club_names = set()
    for transfer in transfer_data['transfers']:
        club_names.add(transfer['from']['clubName'])
        club_names.add(transfer['to']['clubName'])
        
    return(club_names)

# Get list of all clubs in Europe's top 5 leauges 
def get_top5_league_clubs():
    """
    Function to scrape the names of top 5 European league clubs from the provided URL.

    Returns:
        squad_data (list): A list containing the names of the clubs from the 'squad' column.
    """
    url = "https://fbref.com/en/comps/Big5/Big-5-European-Leagues-Stats"
    
    # Send a GET request to the URL and parse the HTML content
    response = requests.get(url, headers=headers.headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the table with the specified class
    table = soup.select_one('#big5_table > tbody')

    # Extract data from the 'squad' column
    squad_data = []
    rows = table.find_all('tr')
    for row in rows:
        # Find the 'td' element in the first column (index 0)
        squad_cell = row.find_all('td')[0]
        squad_value = squad_cell.get_text(strip=True)  # Extract the text of the cell
        squad_data.append(squad_value)
        
    return squad_data

# Get list of 25 most valuable clubs according to TransferMarkt
def get_top25_clubs_tmarkt() :
    
    url = 'https://www.transfermarkt.co.uk/spieler-statistik/wertvollstemannschaften/marktwertetop'
    # Send a GET request to the URL
    response = requests.get(url, headers = headers.headers)

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the specified element
    element = soup.select_one('#yw1 > table > tbody')
    
    clubs = re.findall(r'\/saison_id\/2023\" title=\"(.*?)\">', str(element))
    clubs = [text.replace("&amp;", "and") for text in clubs]
    clubs = [text.replace("FC ", "") for text in clubs]
    clubs = [text.replace(" FC", "") for text in clubs]    
    clubs = [text.replace("Saint-Germain", "SG") for text in clubs]
    clubs = [text.replace("Hotspur", "") for text in clubs]
    clubs = [text.replace("United", "Utd") for text in clubs]
    
    return(clubs)

# Does TransferMarkt player history match the arbitrary club

def return_club_match(player_clubs, club1, club2):
    """
    Check if both clubs are present in the list of player clubs with a similarity score of at least 70.

    Args:
        player_clubs (list): A set or list containing the player's clubs.
        club1 (str): The first club to compare.
        club2 (str): The second club to compare.

    Returns:
        bool: True if both clubs are present in the player's clubs list with a similarity score of at least 70, 
        False otherwise.
    """
    # Create a list containing the two clubs to compare
    club_intersection = [club1, club2]
    
    # Convert player_clubs to a list if it's not already
    player_club_list = list(player_clubs)
    
    # Initialize an empty list to store match results
    match = []
    
    # Iterate over the clubs to compare
    for j in club_intersection:
        max_ratio = []
        # Calculate similarity scores for each player's club
        for i in player_club_list:
            similarity_score = fuzz.ratio(j, i)
            max_ratio.append(similarity_score)
        # Check if the maximum similarity score is less than 70
        if max(max_ratio) < 70:
            match.append(False)
        else:
            match.append(True)
    
    # Check if all match results are True
    if all(match):
        return True
    else:
        return False
