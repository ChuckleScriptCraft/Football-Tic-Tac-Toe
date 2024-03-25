# Package
library(tidyverse)
library(worldfootballR)
library(rvest)
library(snakecase)


# Get mappings
map_plyr = player_dictionary_mapping()

check_player_club <- function(player, guess){
  
  # Make sure player case matches mapping
  player = to_title_case(player)
  
  # Get URL of player
  player_fb = map_plyr %>% filter(PlayerFBref == player) %>% 
    pull(UrlFBref)
  
  # Stop under condition
  if(length(player_fb) == 0){
    stop("Unknown Player Name")
  }
  
  # Read in html page data
  page = read_html(player_fb)
  
  # Retrieve table
  element <- page %>% 
    html_nodes("#div_stats_misc_dom_lg")%>% 
    html_table() %>% 
    as.data.frame() 
  
  # Clean table
  clean_table <- element %>% 
    setNames(.[1, ]) %>%   
    slice(-1) %>% 
    select(Squad) %>% 
    filter(!grepl("U[0-9]{2}\\b", Squad)) %>%  # Remove youth clubs
    unique()
  
  # Identify where to slice vector  
  empty_row_index <- which.max(apply(clean_table == "", 1, all))
  
  # Remove identified index
  clubs <- clean_table[seq_len(empty_row_index - 2), ] 
  
  # Does guess match?
  match = to_title_case(guess) %in% clubs
  
  # If no match:
  if(!match){
    cat(player, "has not played for", guess, "\nHe has played for:",
        paste(clubs, collapse = ", "),"\n\n")
    
    return(F)
  } else if(match){
    return(T)
  }
  
}


