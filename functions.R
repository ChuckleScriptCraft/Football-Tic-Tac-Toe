# Package
library(tidyverse)
library(worldfootballR)
library(rvest)
library(snakecase)


# Get mappings
map_plyr = player_dictionary_mapping()

# FBRef Club Checker
check_player_club_fbref <- function(player, guess){
  
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
  match <- to_title_case(guess) %in% clubs
  
  # If no match:
  if(!match){
    cat(player, "has not played for", guess, "\nHe has played for:",
        paste(clubs, collapse = ", "),"\n\n")
    
    return(F)
  } else if(match){
    return(T)
  }
  
}

# Wikipedia Club Checker
## Has some benefits where mappings are missing
check_player_club_wikipedia <- function(player, guess){
  
  # Upper snake case conversion
  player_name <- str_to_title(player) %>% gsub("\\s", "_", .)
  
  # Save URL as object (assumes consisent naming convention)
  url = paste0("https://en.wikipedia.org/wiki/", player_name) 
  
  # Read page
  page <- read_html(url)
  
  # Extract the content of the info box section
  career_infobox <- page %>%
    html_nodes(".infobox") %>%
    html_table(fill = TRUE)
  
  # Convert to dataframe
  data <- career_infobox[[1]] %>% 
    as.data.frame()
  
  # Perform cleaning
  cleaned_data <- lapply(data, function(x) gsub("[[:punct:]]|[^[:alnum:][:space:]]", "", x)) %>% 
    as.data.frame()
    
  # Find index where relevant section starts
  ## Min index
  index <- which(cleaned_data$X1 == "Senior career")
  
  ## Max index
  ### All numerical values
  index_pre1 <- which(grepl("^\\d+$", cleaned_data$X1))
  
  ### All numerical values greater than smallest row index
  index_pre2 <- index_pre1[index_pre1 > index]
  
  # Minimum index which is not part of sequence from smallest to largest index value
  max_row <- seq(min(index_pre2),max(index_pre2))[!seq(min(index_pre2),max(index_pre2)) %in% index_pre1]
  
  # Row index to filter on
  index_max <- max(index_pre2[index_pre2<max_row])
  
  # Filter indices
  club_data <- cleaned_data[(index+1):index_max,] %>% as.data.frame() 
  
  # Find Clubs
  clubs <- club_data %>% setNames(.[1, ]) %>% 
    select(Team) %>% 
    slice(-1) %>% 
    mutate(Team = gsub("(?i)loan", "", Team)) %>% 
    pull(Team) %>% trimws() %>% 
    unique()
  
  
  # Does guess match?
  match <- to_title_case(guess) %in% clubs
  
  # If no match:
  if(!match){
    cat(player, "has not played for", guess, "\nHe has played for:",
        paste(clubs, collapse = ", "),"\n\n")
    
    return(F)
  } else if(match){
    return(T)
  }
  
}