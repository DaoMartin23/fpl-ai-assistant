import os
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score
# modules used for machine learning algorithm
import joblib # module used for storing and loading files

from src.entities import Player, Goalkeeper, Club


# a function to train the random forest model for defenders, taking in the player and club object arrays as parameters

def train_random_forest_defender(players,clubs,models_dir):
    x = []
    y= []
    team = ""
    data = []

    # loops through the players, selecting defenders and their correct clubs

    for player in players:
        for club in clubs:
            if club.team == "Ipswich Town":
                team = "Ipswich"
            else:
                team = club.team
            if team == player.team and player.position == "DEF":

                # the Player and Club methods are used to retrieve the training data and they are joined together

                data = Player.return_training_data_defender(player) + Club.return_training_data_defender(club)
                x.append(data)

                # the Player method returns the models training target
                y.append(Player.return_training_target(player))

    # The Sk Learn module is used here to train the model

    # The x and y values are plotted using the training and target data, with a test sized used of 10% to evaluate the model

    X_train, X_test, Y_train, Y_test = train_test_split(x, y, test_size=0.1, random_state=42)

    # The model is set using parameters which have been tested to maximise the performance of the positions model

    model = RandomForestRegressor(n_estimators=250, max_depth=20, min_samples_split=2, min_samples_leaf=4,random_state=42)
    model.fit(X_train, Y_train)

    # these lines of code are used for evaluating the models effectiveness and fit

    predictions = model.predict(X_test) # predictions for the training data is created
    mse = mean_squared_error(Y_test, predictions) # prediction is compared to the result and a MSE value is produced
    r2 = r2_score(Y_test,predictions) # prediction is compared to the result and a R2 score is produced
    print("Testing for Defender prediction:")
    print(f"R² Score: {r2}")
    print(mse, "\n")
    joblib.dump(model, os.path.join(models_dir, "DEF_Prediction.pkl")) # the model is than stored into a pickle file so it does not need to be retrained


# This process is repeated for all positions. Different parameters for the model is used for each to maximise effectiveness.

# training the midfielder model

def train_random_forest_midfielder(players,clubs,models_dir):
    x = []
    y= []
    team = ""
    data = []
    for player in players:
        for club in clubs:
            if club.team == "Ipswich Town":
                team = "Ipswich"
            else:
                team = club.team
            if team == player.team and player.position == "MID":
                data = Player.return_training_data(player) + Club.return_training_data(club)
                x.append(data)
                y.append(Player.return_training_target(player))


    X_train, X_test, Y_train, Y_test = train_test_split(x, y, test_size=0.3, random_state=42)
    model = RandomForestRegressor(n_estimators=150, max_depth=10, min_samples_split=15, min_samples_leaf=5,random_state=42)
    model.fit(X_train, Y_train)
    predictions = model.predict(X_test)
    mse = mean_squared_error(Y_test, predictions)
    r2 = r2_score(Y_test,predictions)
    print("Testing for Midfielder prediction:")
    print(f"R² Score: {r2}")
    print(mse, "\n")
    joblib.dump(model, os.path.join(models_dir, "MID_Prediction.pkl"))

# training the attacker model

def train_random_forest_attacker(players,clubs,models_dir):
    x = []
    y= []
    team = ""
    data = []
    for player in players:
        for club in clubs:
            if club.team == "Ipswich Town":
                team = "Ipswich"
            else:
                team = club.team
            if team == player.team and player.position == "ATT":
                data = Player.return_training_data(player) + Club.return_training_data(club)
                x.append(data)
                y.append(Player.return_training_target(player))


    X_train, X_test, Y_train, Y_test = train_test_split(x, y, test_size=0.1, random_state=42)
    model = RandomForestRegressor(n_estimators=150, max_depth=None, min_samples_split=10, min_samples_leaf=2,random_state=42)
    model.fit(X_train, Y_train)
    predictions = model.predict(X_test)
    mse = mean_squared_error(Y_test, predictions)
    r2 = r2_score(Y_test,predictions)
    print("Testing for Attacker prediction:")
    print(f"R² Score: {r2}")
    print(mse, "\n")
    joblib.dump(model, os.path.join(models_dir, "ATT_Prediction.pkl"))

# training the goalkeeper model

def train_random_forest_goalkeeper(players,clubs,models_dir):
    x = []
    y= []
    team = ""
    data = []
    for player in players:
        for club in clubs:
            if club.team == "Ipswich Town":
                team = "Ipswich"
            else:
                team = club.team
            if team == player.team and player.position == "GK":
                data = Goalkeeper.return_training_data(player) + Club.return_training_data_goalkeeper(club)
                x.append(data)
                y.append(Player.return_training_target(player))


    X_train, X_test, Y_train, Y_test = train_test_split(x, y, test_size=0.3, random_state=42)
    model = RandomForestRegressor(n_estimators=200, max_depth=None, min_samples_split=5, min_samples_leaf=2,random_state=42)
    model.fit(X_train, Y_train)
    predictions = model.predict(X_test)
    mse = mean_squared_error(Y_test, predictions)
    r2 = r2_score(Y_test,predictions)
    print("Testing for Goalkeeer prediction:")
    print(f"R² Score: {r2}")
    print(mse, "\n")
    joblib.dump(model, os.path.join(models_dir, "GK_Prediction.pkl"))
