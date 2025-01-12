import streamlit as st
from pathlib import Path
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.utilities import SQLDatabase
from langchain.agents.agent_types import AgentType
from langchain.callbacks import StreamlitCallbackHandler
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from sqlalchemy import create_engine
import sqlite3
import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import urllib.parse
import ngrok

load_dotenv()

st.set_page_config(page_title = "LangChain: Chat with SQL DB", page_icon="🦜")
st.title("🦜 LangChain: Chat with SQL DB")

LOCALDB = "USE_LOCALDB"
MYSQL = "USE_MYSQL"

radio_opt = ["Use SQLite3 Database - student.db", "Connect to your MySQL Database"]

selected_opt = st.sidebar.radio(label = "Choose the DB you want to interact with", options = radio_opt)


def clear_inputs():
    print("here123")
    st.session_state["mysql_host"] = ""
    st.session_state["mysql_user"] = ""
    st.session_state["mysql_password"] = ""
    st.session_state["mysql_db"] = ""

if radio_opt.index(selected_opt) == 1:
    db_uri = MYSQL
    tunnel_conn = st.sidebar.checkbox("Tunnel connection", on_change=clear_inputs)
    mysql_host = st.sidebar.text_input("Provide MySQL Host Name", key="mysql_host")
    mysql_user = st.sidebar.text_input("MYSQL User Name", key="mysql_user")
    mysql_password = st.sidebar.text_input("MYSQL Password", type = "password", key="mysql_password")
    mysql_db = st.sidebar.text_input("MySQL Database Name", key="mysql_db")
else:
    db_uri = LOCALDB

api_key = os.getenv("GROQ_API_KEY")

if not db_uri:
    st.info("Please enter the database information and uri")

if not api_key:
    st.info("Please add the groq api key")

# LLM model
llm = ChatGroq(groq_api_key = api_key, model_name = "llama3-70b-8192", streaming = True)

@st.cache_resource(ttl = "2h")
def configure_db(db_uri, mysql_host = None, mysql_user = None, mysql_password = None, mysql_db = None):
    if db_uri == LOCALDB:
        dbfilepath=(Path(__file__).parent/"student.db").absolute()
        print(dbfilepath)
        creator = lambda: sqlite3.connect(f"file:{dbfilepath}?mode=ro", uri = True)
        return SQLDatabase(create_engine("sqlite:///", creator = creator))
    elif db_uri == MYSQL:
        if not (mysql_host and mysql_user and mysql_password and mysql_db):
            st.error("Please provide all MySQL connection details!")
            st.stop()
        if tunnel_conn:
            listener = ngrok.forward(3306, "tcp", authtoken_from_env=True)
            mysql_host = listener.url().replace("tcp://", "")
        connection_str = f"mysql+mysqlconnector://{mysql_user}:{urllib.parse.quote_plus(mysql_password)}@{mysql_host}/{mysql_db}"
        return SQLDatabase(create_engine(connection_str))   
    
if db_uri == MYSQL:
    db = configure_db(db_uri, mysql_host, mysql_user, mysql_password, mysql_db)
else:
    db = configure_db(db_uri)

## SQLToolkit
toolkit = SQLDatabaseToolkit(db = db, llm = llm)

agent = create_sql_agent(
    llm = llm,
    toolkit = toolkit,
    verbose = True,
    agent_type = AgentType.ZERO_SHOT_REACT_DESCRIPTION
)

if "messages" not in st.session_state or st.sidebar.button("Clear message history"):
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_query = st.chat_input(placeholder = "Ask anything from the database")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    st.chat_message("user").write(user_query)

    with st.chat_message("assistant"):
        streamlit_callback = StreamlitCallbackHandler(st.container())
        response = agent.run(user_query, callbacks = [streamlit_callback])
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.write(response)
