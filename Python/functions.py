# Packages
import requests
from bs4 import BeautifulSoup


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
    modified_list = set(squad[2:index_of_blank])
    
    return(modified_list)  

