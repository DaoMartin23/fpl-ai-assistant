import requests # module used for webscraping
import pandas as pd # module used for manipulating datasets
import time # module used for implementing timers

from src.config import FOOTBALL_DATA_API_KEY, CURRENT_SEASON_START_YEAR


# function used to webscrape FPL data directly from the website

def get_fplData(): # defining the function to fetch FPL specific data

    # requests the html from the stored URL and parses the content to manipulate the data to be readable
    fpl_url = "https://fantasy.premierleague.com/api/bootstrap-static/"
    fpl_data = requests.get(fpl_url).json()

    # selects the required data for players and creates a dataframe with the information
    players = fpl_data["elements"]
    players_df = pd.DataFrame(players)


    players_df = players_df[players_df["minutes"] > 0]  # filters for players with more than 0 minutes played


    player_stats = [] # initiates an empty list for the players


    for player in players_df.itertuples():  #loops through each individual player

        # stores each players stats into variables

        player_name = player.web_name
        player_id = player.id
        player_price = player.now_cost / 10
        player_total_points = player.total_points
        player_minutes = player.minutes

        # uses a dictionary of player positions to convert element types into FPL positions

        player_position = {
            1: "GK",
            2: "DEF",
            3: "MID",
            4: "ATT"
        }[player.element_type]
        player_expected_conceded = player.expected_goals_conceded
        player_conceded = player.goals_conceded
        player_saves = player.saves

        # requests the information of a different website holding the past points of players and parses data

        points_url = f"https://fantasy.premierleague.com/api/element-summary/{player_id}/"
        points_data = requests.get(points_url).json()

        # searches for the past points of players stored "history" in the webpage

        if "history" in points_data:
            history = points_data["history"]

            # stores the points of the player for the past 5 weeks

            last_5_weeks = history[-5:]
            last_5_points = [week["total_points"] for week in last_5_weeks]

            # check for whether the player has a point tally for the past 5 weeks. Otherwise "null" result will tamper with the Random Forest algorithm.
            # this is needed for newly transfered players to the Premier League

            if len(last_5_points) != 5:
                for i in range(5-len(last_5_points)):
                    last_5_points.append(0)  # if statement to fill array of points with '0' if the player does not have 5 past results



            # adds a dictionary of all the players stats to the 'player_stats' array

            player_stats.append({
                "Player Name": player_name,
                "Price": player_price,
                "Total Points": player_total_points,
                "Minutes Played": player_minutes,
                "Player Position": player_position,
                "Expected Conceded": player_expected_conceded,
                "Conceded": player_conceded,
                "Saves": player_saves,
                "1 Week Points": last_5_points[0] ,
                "2 Week Points": last_5_points[1] ,
                "3 Week Points": last_5_points[2] ,
                "4 Week Points": last_5_points[3] ,
                "5 Week Points": last_5_points[4]
            })


    fpl_df = pd.DataFrame(player_stats) # converts the array into a dataframe for easy manipulation
    return(fpl_df) # returns the dataframe




def get_understatData():  # defines an array to fetch the rest of the player data from the 'Understat' website

    # Understat used to embed a "playersData" JSON blob directly in the page HTML, which the original
    # version of this function extracted with BeautifulSoup. Understat has since moved this data behind
    # an internal AJAX endpoint instead, so it's fetched directly as JSON here.
    understat_url = f"https://understat.com/getLeagueData/EPL/{CURRENT_SEASON_START_YEAR}"

    # the X-Requested-With header is required by Understat's server for this endpoint;
    # a plain browser-style request to it returns a 404
    understat_response = requests.get(understat_url, headers={"X-Requested-With": "XMLHttpRequest"})
    understat_response.raise_for_status()
    player_data = understat_response.json()["players"]

    understat_players = [] # initialises an empty array for the players

    # loops through the players in the data

    for player in player_data:

        # solves issue of players who have played for multiple clubs this season. Splits the string of clubs by the comma
        team = ""
        if "," in player["team_title"]:
            team = player["team_title"][:player["team_title"].index(",")]
            # selects only the most recent club the player has played for
        else:
            team = player["team_title"]

        # uses a dictionary to store all of the players data

        understat_players.append({
            "Player Name": player["player_name"],
            "Team": team,
            "Games Played": player["games"],
            "Goals": player["goals"],
            "xG": player["xG"],
            "Assists": player["assists"],
            "xA": player["xA"],
            "Shots": player["shots"],
            "Key Passes": player["key_passes"]
        })

    # converts the array into a dataframe for easy manipulation

    understat_df = pd.DataFrame(understat_players)

    return(understat_df) # returns the dataframe


# stores the URLS for club fixtures and past result from the 'football-data.org' API

Results_URL = 'https://api.football-data.org/v4/competitions/PL/standings'
Fixtures_URL = 'https://api.football-data.org/v4/teams/{}/matches'


headers = {
    'X-Auth-Token': FOOTBALL_DATA_API_KEY
}

def get_fixtures(team_id): # defines a function for fetching the future fixtures of clubs
    next_fixtures = [] # initialises an empty array for the club fixtures

    # parameters for what we want to fetch from the API

    params = {
        'status': 'SCHEDULED',  # Only fixtures which have finished will be fetched
        'limit': 10,   # 10 of the next fixtures will be fetched as not all of the fixtures will be Prem Matches
    }

    # requests the data for those parameters and parses the information

    try:
        response = requests.get(Fixtures_URL.format(team_id), headers=headers, params=params)
        response.raise_for_status()
        fixtures = response.json()

        # loops through all the matches in the fetched fixtures

        for match in fixtures['matches']:

            # stores which teams are Home and Away teams in that match

            if match['competition']['code'] == 'PL':  # filters for only Premier League matches
                home_team = match['homeTeam']['name']
                away_team = match['awayTeam']['name']

                # uses an if statement to check whether the home or away team is the team we are fetching data for
                # adds the other team to the future fixtures array

                if match['homeTeam']['id'] == team_id:
                    next_fixtures.append(away_team)
                else:
                    next_fixtures.append(home_team)

                # ends the loop when 3 fixtures have been added

                if len(next_fixtures) == 3:
                    break

    except requests.exceptions.RequestException as error:  # exception handling which tells you which team's data can not be fetched
        print(f"Couldnt get data for {team_id}: {error}")

    return next_fixtures

# process is repeated for the results

def get_results(team_id):
    results = []

    params = {
        'status': 'FINISHED',
        'limit': 10,
    }

    try:
        response = requests.get(Fixtures_URL.format(team_id), headers=headers, params=params)
        response.raise_for_status()
        fixtures = response.json()

        for match in fixtures['matches']:

            if match['competition']['code'] == 'PL':
                home_team = match['homeTeam']['name']
                away_team = match['awayTeam']['name']


                if match['homeTeam']['id'] == team_id:
                    results.append(away_team)
                else:
                    results.append(home_team)

                # ends the loop once the last 5 results have been added

                if len(results) == 5:
                    break

    except requests.exceptions.RequestException as error:
        print(f"Couldnt get results for {team_id}: {error}")

    return results

# defines a function to get the rest of the clubs data

def get_premier_league_data():

    teams_data = [] # initialises an empty array for the club's data
    standings_params = {'season': CURRENT_SEASON_START_YEAR } # selects the current season, so standings stay in sync with the current fixtures/results fetched below


    try: # attempts to fetch the data from the API and parse
        response = requests.get(Results_URL, headers=headers, params=standings_params)
        response.raise_for_status()

        standings = response.json()
        for team in standings['standings'][0]['table']:  # loops through the teams in the prem table

            # stores all the clubs stats into variables

            team_id = team['team']['id']
            team_name = team['team']['name']
            points = team['points']
            games_played = team['playedGames']
            goals_for = team['goalsFor']
            goals_against = team['goalsAgainst']

            # calls the subroutines which will fetch the results and fixtures of the clubs and stores them into variables

            fixtures_future = get_fixtures(team_id)
            fixtures_past = get_results(team_id)

            # creates a dictionary with all the clubs data and adds it to the teams data array

            teams_data.append({
                "Team Name": team_name,
                "Points": points,
                "Games Played": games_played,
                "Goals For": goals_for,
                "Goals Against": goals_against,
                "Last Fixture": fixtures_past[4],
                "Last Fixture 1": fixtures_past[3],
                "Last Fixture 2": fixtures_past[2],
                "Last Fixture 3": fixtures_past[1],
                "Last Fixture 4": fixtures_past[0],
                "Next Fixture": fixtures_future[0],
                "Next Fixture 1": fixtures_future[1],
                "Next Fixture 2": fixtures_future[2]
            })


            time.sleep(15) # uses time module to delay API requests by 15 seconds as to not go past the limit

    except requests.exceptions.RequestException as error:  # exception handling to provide an appropriate error message
        print(f"Couldnt get data: {error}")


    teams_df = pd.DataFrame(teams_data) # turns the dictionary into a dataframe

    # fixes the problem of club names from the Understat and Premier League website being different

    # an array of the columns which need to be fixed

    team_columns = ["Team Name", "Last Fixture", "Last Fixture 1", "Last Fixture 2", "Last Fixture 3", "Last Fixture 4", "Next Fixture", "Next Fixture 1", "Next Fixture 2"]

    for columns in team_columns: # loops through the columns

        # corrects all the team names for the required columns

        teams_df[columns] = teams_df[columns].replace({'AFC Bournemouth': 'Bournemouth'})
        teams_df[columns] = teams_df[columns].replace({'Brighton & Hove Albion FC': 'Brighton'})
        teams_df[columns] = teams_df[columns].replace({'Tottenham Hotspur FC': 'Tottenham'})
        teams_df[columns] = teams_df[columns].replace({'West Ham United FC': 'West Ham'})
        teams_df[columns] = teams_df[columns].replace({'Ipswich Town': 'Ipswich'})
        teams_df[columns] = teams_df[columns].replace({'Leicester City FC': 'Leicester'})
        teams_df[columns] = teams_df[columns].str.replace(' FC', '')
    return teams_df # returns the dataframe
