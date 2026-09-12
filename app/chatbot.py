
# langchain imports used for chatbot creation

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # allows "from src.config import ..." when run via `streamlit run`

from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain.agents import AgentType
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit

import streamlit as st # module imported for web app development

from src.config import DB_PATH, OPENAI_API_KEY


SQLDatabaseToolkit.model_rebuild() # used to reset the model as blank

# an array of common queries which suggest a RAG approach to answering queries will be best

common_database_queries = ["price", "points", "goals", "assists", "xg", "xa", "games played", "shots", "key passes", "minutes", "position",
                           "conceded", "expected", "saves", "predicted", "points", "fixture", "next", "last", "place", "attacker", "defender",
                             "midfielder", "goalkeeper", "best", "gameweek", "goalscorer"]

# the database schema is created through the directory path

database = SQLDatabase.from_uri(f"sqlite:///{DB_PATH}")

# the llm model and API key are defined

llm = ChatOpenAI(model="gpt-4o", openai_api_key=OPENAI_API_KEY)
sql_toolkit = SQLDatabaseToolkit(db=database,llm=llm)
sql_toolkit.get_tools()

# the ai langchain agent is created for RAG querying the database
sqldb_agent = create_sql_agent(llm=llm, toolkit=sql_toolkit, agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=False, handle_parsing_errors=True)


# a function used to query the llm/ai agent

def query_assistant(user_query): # takes a user query in as input
    user_query = user_query.split() # the query is split up into words
    response = ""
    use_rag = False
    for words in user_query: # looping throught the words in the query
        if words in common_database_queries:
            use_rag = True  # confirming RAG approach since the query contains commonly used terms
    user_query = (" ").join(user_query)
    if use_rag == True:
        response = sqldb_agent.invoke(user_query)["output"] # uses the ai agent to produce a response from the database
    else:
        response = llm.invoke(user_query).content  # uses the llm to provide a response
    return(response)


# following lines are used to create the GUI that the user will interact with


phrase = "AI FPL Assistant ⚽️"
title = st.title(phrase)  # creates the title page of the web app
subtitle = st.subheader("Your personal assistant for all things FPL")  # subtitle for the web app
st.divider()  # dividers are used to nicely format queries and responses
st.text("⚽️ - Ask me anything FPL related that you fancy! Enter 'Bye' to exit.")

talking = True
user_input = st.chat_input("Ask me here ...")  # takes in a user input and stores to a variable
st.divider()
if user_input:
    st.text(f"{str(user_input)}-👤")  # prints the user input
    user_input = str(user_input).lower()  # converts the input into lowercase
    st.divider()
    if user_input == "bye":
        st.text("⚽️-Bye!")  # respondes with 'bye' if the user prompts to leave
    else:
        st.text(f"⚽️-{query_assistant(user_input)}")  # if not, the query goes through to the agent/llm and a response is printed
