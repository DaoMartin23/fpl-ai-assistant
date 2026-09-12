import pandas as pd # module used for manipulating datasets
from fuzzywuzzy import process # module used for matching close phrases


# subroutine to turn all player names into first name initial followed by last names
# this helps the issue of player names being different between websites

def get_initials(name):
    names_seperated = name.split() # creates an array with the first name and last name by splitting it through the space
    for i in range(len(names_seperated)-1): # loops through the list
        names_seperated[i] = names_seperated[i][0] + "."  # gets the first initial of the first name and concatenates it with a '.'
    names_joined = "".join(names_seperated) # joins the initial back with the last name
    return names_joined

# a subroutine to normalise the name by converting it to lower case and removing trailing spaces

def normalise_name(name):
    return name.strip().lower()

# defines a subroutine to merge all of the previously created  dataframes

def merge_dataframes(understat_df,fpl_df): # takes in the two player dataframes as parameters

    # calls the normalise name and get initial functions to the 'Player Name' columns of the dataframe

    understat_df["Player Name"] = understat_df["Player Name"].apply(get_initials)

    fpl_df["Player Name"] = fpl_df["Player Name"].apply(normalise_name)
    understat_df["Player Name"] = understat_df["Player Name"].apply(normalise_name)

    # uses the 'FuzzyWuzzy' module to roughly match player names that are formatted differently
    name_matching = {}
    for understat_name in understat_df["Player Name"]: # loops through the names
        match = process.extractOne(understat_name, fpl_df["Player Name"]) # gets a matching 'score' between the names in the dataframes
        if match and match[1] > 86:  # uses an if statements to select the names that are an 86% match
            name_matching[understat_name] = match[0]

    # replaces the player names from the understat dataframe with the ones in the FPL dataframe if they 'match'

    understat_df["FPL Name"] = understat_df["Player Name"].map(name_matching)

     # merges the two dataframes through the player name column

    merged_df = pd.merge(fpl_df, understat_df, left_on="Player Name", right_on="FPL Name", how="inner")


    merged_df.drop(columns=["FPL Name", "Player Name_x"], inplace=True) # drops unneccesary columns
    merged_df.rename(columns={"Player Name_y": "Player Name"}, inplace=True)
    return(merged_df) # returns the merged dataframe
