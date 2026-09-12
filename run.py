import os  
import subprocess

import build_database  # builds the database and trains the prediction models

build_database.main()

subprocess.run(["streamlit", "run", os.path.join("app", "chatbot.py")])  # launches the Chatbot and GUI
