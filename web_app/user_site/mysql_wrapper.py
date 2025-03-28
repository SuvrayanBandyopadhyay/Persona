import mysql.connector
import streamlit as st

conn = mysql.connector.connect(**st.secrets.mysql)
cursor = conn.cursor(dictionary=True)