import os
import joblib # module used for storing and loading files

from src.config import MODELS_DIR

# populated by build_database.py with the list of Club objects for the season
# kept as a module-level list (rather than a parameter) to preserve the original
# design, where Player/Goalkeeper prediction methods look club data up directly
clubs = []


# a method used to convert the premierleague clubs into numbers so that they can be used as factors in the Random Forest Model
def club_to_numbers(club_name):
    clubs_numbers = {"Liverpool" : 0, "Arsenal" : 1, "Nottingham Forest" : 2, "Chelsea" : 3,
                      "Newcastle United" : 4, "Manchester City" : 5, "Bournemouth" : 6, "Aston Villa" : 7,
                        "Fulham" : 8, "Brighton" : 9, "Brentford" : 10, "Tottenham" : 11, "West Ham" : 12,
                          "Manchester United" : 13, "Crystal Palace" : 14, "Everton" : 15, "Wolverhampton Wanderers" : 16,
                            "Ipswich Town" : 17, "Ipswich" : 17, "Leicester" : 18, "Southampton" : 19}
    return(clubs_numbers[club_name])


# creating an OOP Player class

class Player:
    # initialising the object with all of the player stats
    def __init__(self, name, team, price, player_points, games_played, minutes, position, week1_points, week2_points, week3_points, week4_points,
                  week5_points, goals, assists, xG, xA, shots, key_passes, conceded, expected_conceded):
        self.name = name
        self.team = team
        self.price = price
        self.player_points = player_points
        self.games_played = games_played
        self.minutes = minutes
        self.position = position
        self.week1_points = week1_points
        self.week2_points = week2_points
        self.week3_points = week3_points
        self.week4_points = week4_points
        self.week5_points = week5_points
        self.goals = goals
        self.assists = assists
        self.xG = xG
        self.xA = xA
        self.shots = shots
        self.key_passes = key_passes
        self.conceded = conceded
        self.expected_conceded = expected_conceded

    # defining a method for retrieving the stats needed to train the Forward/Midfielder Random Forest model

    def return_training_data(self):
        return([club_to_numbers(self.team), self.player_points, self.minutes, self.week2_points, self.week3_points, self.week4_points,
                 self.week5_points, self.goals, self.assists, self.xG, self.xA, self.shots, self.key_passes])

    # defining a method for retrieving the stats needed to train the Defender Random Forest model

    def return_training_data_defender(self):
        return([club_to_numbers(self.team), self.player_points, self.minutes, self.week2_points, self.week3_points,
                 self.week4_points, self.week5_points, self.goals, self.assists, self.xG, self.xA, self.shots, self.key_passes,self.conceded,self.expected_conceded])

    # a method for retrieving the models training target value

    def return_training_target(self):
        return(self.week1_points)

    # a method to call upon the Random Forest model and get a prediction for points

    def get_prediction(self):
        prediction_file = os.path.join(MODELS_DIR, str(self.position) + "_Prediction.pkl")  # uses concatenation to select which pickle file to use for the position
        prediction_model = joblib.load(prediction_file) # uses the joblib module to load the contents of the file into a variable
        prediction_data = []
        club_data = []
        club_name = ""
        for club in clubs:
            if club.team == "Ipswich Town":
                club_name = "Ipswich"
            else:
                club_name = club.team
            if club_name == self.team:

                # if the player is a defender, the defender data is collected

                if self.position == "DEF":

                # calls upon club objects and uses it's method to collect relevant defender stats from that club

                    club_data = Club.get_prediction_data_defender(club)
                else:
                    club_data = Club.get_prediction_data(club) # gets normal stats for midfielders and defenders

        # depending on position, the relevant club and player stats are combined and stored as a single array

        if self.position == "DEF":
            prediction_data = [[club_to_numbers(self.team), self.player_points, self.minutes, self.week1_points, self.week2_points,
                                 self.week3_points, self.week4_points, self.goals, self.assists, self.xG, self.xA, self.shots,
                                   self.key_passes,self.conceded,self.expected_conceded]+ club_data]
        else:
            prediction_data = [[club_to_numbers(self.team), self.player_points, self.minutes, self.week1_points, self.week2_points,
                                 self.week3_points, self.week4_points, self.goals, self.assists, self.xG, self.xA, self.shots, self.key_passes]+ club_data]

        # the prediction model is used, with the combined stats as its inout values, and the predicted points for the player is returned

        prediction_points = prediction_model.predict(prediction_data)
        return(prediction_points)

# creates a seperate Goalkeeper class which is a child class to it's parent Player Class

class Goalkeeper(Player):

    # initialises all the goalkeeper stats to the object
    # inheritance is used to initialise some of the attributes while adding other goalkeeper specific ones on top

    def __init__(self, name, team, price, player_points, games_played, minutes, position, week1_points, week2_points,
                  week3_points, week4_points, week5_points, conceded, expected_conceded, saves):
        super().__init__(name, team, price, player_points, games_played, minutes, position, week1_points, week2_points,
                          week3_points, week4_points, week5_points, goals=0, assists=0, xG=0.0, xA=0.0, shots=0, key_passes=0,
                            conceded=conceded, expected_conceded=expected_conceded)
        self.saves = saves

    # method used to retrieve the training data needed for the goalkeeper Random Forest model
    # polymorphism used to return a different set of stats for a goalkeeper compared to other positions

    def return_training_data(self):
        return([club_to_numbers(self.team), self.player_points, self.minutes, self.week2_points, self.week3_points, self.week4_points,self.conceded,self.expected_conceded,self.saves])

    # method used to get a prediction for the goalkeepers points next gameweek

    def get_prediction(self):
        prediction_file = os.path.join(MODELS_DIR, "GK_Prediction.pkl")
        prediction_model = joblib.load(prediction_file)  # loads the goalkeeper pickle file with the model
        club_data = []
        club_name = ""
        for club in clubs:
            if club.team == "Ipswich Town":
                club_name = "Ipswich"
            else:
                club_name = club.team
            if club_name == self.team:

                # uses the Club class' method for retrieving the needed club raining stats for goalkeepers

                club_data = Club.get_prediction_data_goalkeeper(club)

        # joins the goalkeeper and clubs stats

        prediction_data = [[club_to_numbers(self.team), self.player_points, self.minutes, self.week1_points, self.week2_points, self.week3_points,
                            self.conceded,self.expected_conceded,self.saves]+club_data]

        # loads the prediction data into the model as an input and returns the predicted points of the goalkeeper
        prediction_points = prediction_model.predict(prediction_data)
        return(prediction_points)


# Creates a class for Premier League clubs

class Club:

    # initialises the objects with all the club stats

    def __init__(self, team, club_points, games_played, goals_for, goals_against, last_fixture, last_fixture_1, last_fixture_2, last_fixture_3,
                  last_fixture_4, next_fixture, next_fixture_1, next_fixture_2):
        self.team = team
        self.club_points = club_points
        self.games_played = games_played
        self.goals_for = goals_for
        self.goals_against = goals_against
        self.last_fixture = last_fixture
        self.last_fixture_1 = last_fixture_1
        self.last_fixture_2 = last_fixture_2
        self.last_fixture_3 = last_fixture_3
        self.last_fixture_4 = last_fixture_4
        self.next_fixture = next_fixture
        self.next_fixture_1 = next_fixture_1
        self.next_fixture_2 = next_fixture_2

    # different methods for returning the Random Forest training data for each position

    def return_training_data(self):
        return ([self.goals_for,club_to_numbers(self.last_fixture),self.club_points])

    def return_training_data_defender(self):
        return ([self.goals_for,club_to_numbers(self.last_fixture),self.goals_against,self.club_points])

    def return_training_data_goalkeeper(self):
        return ([club_to_numbers(self.last_fixture),self.goals_against,self.club_points])

    # different methods for returning the Random Forest input data for each position

    def get_prediction_data(self):
        return [self.goals_for,club_to_numbers(self.next_fixture),self.club_points]

    def get_prediction_data_defender(self):
        return [self.goals_for,club_to_numbers(self.next_fixture),self.goals_against,self.club_points]

    def get_prediction_data_goalkeeper(self):
        return [club_to_numbers(self.next_fixture),self.goals_against,self.club_points]
