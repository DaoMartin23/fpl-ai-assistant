import sqlite3 

from src.entities import Player, Goalkeeper, Club


# defines a subroutine to create a SQL Database using the merged dataframe and the teams dataframe

def create_database(merged_df, teams_df, db_path):
    conn = sqlite3.connect(db_path)  
    cursor = conn.cursor()

    # creates a table for the club stats using SQL and sets Team Name as the primary key

    cursor.execute("""
        CREATE TABLE club_stats (
            Team_Name TEXT PRIMARY KEY,
            Points INTEGER,
            Games_Played INTEGER,
            Goals_For INTEGER,
            Goals_Against INTEGER,
            Last_Fixture TEXT,
            Last_Fixture_1 TEXT,
            Last_Fixture_2 TEXT,
            Last_Fixture_3 TEXT,
            Last_Fixture_4 TEXT,
            Next_Fixture TEXT,
            Next_Fixture_1 TEXT,
            Next_Fixture_2 TEXT
        )
    """)

    # creates a table for the player stats, setting the team name as a foreign key to link the two tables

    cursor.execute("""
        CREATE TABLE player_stats (
            Player_Name TEXT,
            Team_Name TEXT,
            Price REAL,
            Points INTEGER,
            Goals INTEGER,
            Assists INTEGER,
            xG REAL,
            xA REAL,
            Games_Played INTEGER,
            Shots INTEGER,
            Key_Passes INTEGER,
            Minutes INTEGER,
            Player_Position TEXT,
            Conceded INTEGER,
            Expected_Conceded INTEGER,
            Saves INTEGER,
            Week_1 INTEGER,
            Week_2 INTEGER,
            Week_3 INTEGER,
            Week_4 INTEGER,
            Week_5 INTEGER,
            FOREIGN KEY (Team_Name) REFERENCES club_stats(Team_Name)
        )
    """)

    # more SQL to insert all of the stats into the database tables

    for _, row in merged_df.iterrows(): # loops through the merged dataframe
        cursor.execute("""
            INSERT INTO player_stats (Player_Name, Team_Name, Price, Points, Goals, Assists, xG, xA, Games_Played,
                       Shots, Key_Passes, Minutes, Player_Position, Conceded, Expected_Conceded, Saves,
                        Week_1, Week_2, Week_3, Week_4, Week_5)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row["Player Name"], row["Team"], row["Price"], row["Total Points"], row["Goals"],
            row["Assists"], row["xG"], row["xA"], row["Games Played"], row["Shots"], row["Key Passes"], row["Minutes Played"],
            row["Player Position"], row["Conceded"],row["Expected Conceded"],row["Saves"],
              row["1 Week Points"],row["2 Week Points"],
            row["3 Week Points"],row["4 Week Points"],row["5 Week Points"]
        ))

    for _, row in teams_df.iterrows(): # loops through the merged dataframe
        cursor.execute("""
            INSERT INTO club_stats (Team_name, Points, Games_Played, Goals_For, Goals_Against, Last_Fixture,
                        Last_Fixture_1, Last_Fixture_2,
                       Last_Fixture_3, Last_Fixture_4,Next_Fixture, Next_Fixture_1, Next_Fixture_2)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            row["Team Name"], row["Points"], row["Games Played"], row["Goals For"], row["Goals Against"],
              row["Last Fixture"], row["Last Fixture 1"],
            row["Last Fixture 2"], row["Last Fixture 3"], row["Last Fixture 4"], row["Next Fixture"],
              row["Next Fixture 1"], row["Next Fixture 2"]
        ))

    # saves and closes the connection to the database

    conn.commit()
    conn.close()


# defining a function to create the Player objects from the database information

def player_into_objects(db_name):

    conn = sqlite3.connect(db_name)  
    cursor = conn.cursor()


    cursor.execute("SELECT * FROM player_stats")  # fetches all the player stats
    rows = cursor.fetchall()


    column_names = [desc[0] for desc in cursor.description]  # fetches column names


    players = []
    for row in rows:
        player_data = dict(zip(column_names, row))

        # creates an instance of the goalkeeper class

        if player_data["Player_Position"] == "GK":
            player = Goalkeeper(
                name=player_data["Player_Name"],
                team=player_data["Team_Name"],
                price=player_data["Price"],
                player_points=player_data["Points"],
                games_played=player_data["Games_Played"],
                minutes=player_data["Minutes"],
                position=player_data["Player_Position"],
                week1_points=player_data["Week_1"],
                week2_points=player_data["Week_2"],
                week3_points=player_data["Week_3"],
                week4_points=player_data["Week_4"],
                week5_points=player_data["Week_5"],
                conceded=player_data["Conceded"],
                expected_conceded=player_data["Expected_Conceded"],
                saves=player_data["Saves"]
            )


        # creates an instance of the Player Class

        else:
            player = Player(
                name=player_data["Player_Name"],
                team=player_data["Team_Name"],
                price=player_data["Price"],
                player_points=player_data["Points"],
                games_played=player_data["Games_Played"],
                minutes=player_data["Minutes"],
                position=player_data["Player_Position"],
                week1_points=player_data["Week_1"],
                week2_points=player_data["Week_2"],
                week3_points=player_data["Week_3"],
                week4_points=player_data["Week_4"],
                week5_points=player_data["Week_5"],
                goals=player_data["Goals"],
                assists=player_data["Assists"],
                xG=player_data["xG"],
                xA=player_data["xA"],
                shots=player_data["Shots"],
                key_passes=player_data["Key_Passes"],
                conceded=player_data["Conceded"],
                expected_conceded=player_data["Expected_Conceded"]
            )
        players.append(player)

    # adds all the Player and Goalkeeper objects into an array and retunns it

    conn.close()
    return players

# defines a function to create Club objects from the database information
def clubs_into_objects(db_name):

    conn = sqlite3.connect(db_name) # connects to the database
    cursor = conn.cursor()


    cursor.execute("SELECT * FROM club_stats") # fetches all of the club stats
    rows = cursor.fetchall()


    column_names = [desc[0] for desc in cursor.description]


    clubs = []
    for row in rows:

        # creates an instance of the Club class

        club_data = dict(zip(column_names, row))
        club = Club(
            team=club_data["Team_Name"],
            club_points=club_data["Points"],
            games_played=club_data["Games_Played"],
            goals_for=club_data["Goals_For"],
            goals_against=club_data["Goals_Against"],
            last_fixture=club_data["Last_Fixture"],
            last_fixture_1=club_data["Last_Fixture_1"],
            last_fixture_2=club_data["Last_Fixture_2"],
            last_fixture_3=club_data["Last_Fixture_3"],
            last_fixture_4=club_data["Last_Fixture_4"],
            next_fixture=club_data["Next_Fixture"],
            next_fixture_1=club_data["Next_Fixture_1"],
            next_fixture_2=club_data["Next_Fixture_2"]
        )

        # adds the club objects to an array and returns it

        clubs.append(club)

    conn.close()
    return clubs


# a function used to store all of the predictions back into the database, taking the database and players object array as parameters

def prediction_into_database(database,players):

    conn = sqlite3.connect(database) # connection to the database
    cursor = conn.cursor()

    # SQL is used to add the 'predicted points' column to the players table

    cursor.execute("ALTER TABLE player_stats ADD COLUMN predicted_points REAL")
    prediction_points = 0

    for player in players: # loops through all players

        # Goalkeeper and Player methods are used to retrieve predictions for all the players
        if player.position == "GK":
            prediction_points = float(Goalkeeper.get_prediction(player)[0])
        else:
            prediction_points = float(Player.get_prediction(player)[0])

        # SQL used to update the table by adding all of the prediction data
        cursor.execute("UPDATE player_stats SET predicted_points = ? WHERE Player_Name = ?", (prediction_points,player.name))

    conn.commit()
    conn.close()
