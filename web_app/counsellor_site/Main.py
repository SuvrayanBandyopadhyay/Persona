import streamlit as st
from datetime import datetime
import os
import mysql.connector
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline
from chromadb import PersistentClient

#The connector
connector = mysql.connector.connect(
    host="localhost",
    user="test",
    password="password",
    database="persona"
    )
cursor = connector.cursor()

client = PersistentClient(
    path="../../backend/chroma"
)

# Configure page
st.set_page_config(
    page_title='Persona',
    layout='centered',
    page_icon='🌿',
)



#The session variables
#Get userID and name
if "uID" not in st.session_state:
    st.session_state.uID = 1
    query = "SELECT name from users where uID = %s"
    values = [st.session_state.uID]
    cursor.execute(query,values)
    name = cursor.fetchone()[0]
    st.session_state.name = name
    st.session_state.trend = "Normal"

if "linear" not in st.session_state:
    st.session_state.linear = 0


# Content header
st.title('🌿 Persona Counsellor Dashboard')





# Sidebar with information
with st.sidebar:
    st.title('🌿 Persona')
    st.markdown('''
    ## About
    A friendly, interactive AI powered platform curated to assist students' mental well-being
    
    This dashboard can be used to monitor the mental health of students

    _Made by Team Draco 🐉_
    ''')
    #Select the list of students
    query = "SELECT uID,name from users"
    cursor.execute(query)

    rows = cursor.fetchall()

    options = []
    for row in rows:
        options.append(str(row[0])+" : "+row[1])

    st.markdown(
        '''## Choose a profile'''
    )

    #A drop down menu to select the student
    option = st.selectbox(
    "Name",options
    )
    new_id = options.index(option)+1


    #If we have changed the user
    if(new_id!= st.session_state.uID):
        st.session_state.uID = new_id
        query = "SELECT name from users where uID = %s"
        values = [st.session_state.uID]
        cursor.execute(query,values)
        name = cursor.fetchone()[0]
        st.session_state.name = name

        #Rerun to update
        st.rerun()


#Get overviewdata
query = "SELECT sentiment,count(sentiment) from users,usercon,conmess,messages where users.uID = usercon.uID and usercon.cID = conmess.cID and conmess.mID = messages.mID and users.uID = %s group by sentiment"
values = [st.session_state.uID]
cursor.execute(query,values)
rows = cursor.fetchall()

x =[]
y =[]
#For each row
for row in rows:
    if(row[0]!=None):
        x.append(row[0])
        y.append(row[1])

#The actual information
st.header(f"_{st.session_state.name.title()}_")

#Summary
st.subheader("📝 Summary")
try:
    profile = client.get_collection(f"user_{st.session_state.uID}").get()
    st.markdown("\n\n".join(profile["documents"]))
except:
    st.markdown("_User not yet profiled_")
st.divider()

st.subheader("🥧 Mental State Map")
#Display
fig, ax = plt.subplots()
ax.pie(y,labels=None,autopct='%1.0f%%',pctdistance=1.2)
ax.legend(x, loc="upper left", bbox_to_anchor=(1, 1))  # Move legend outside
st.pyplot(fig)
st.divider()

#Trends
st.subheader("📉 Psychological Trends")

#Get unique sentiments
query = "SELECT DISTINCT(SENTIMENT) FROM users,usercon,conmess,messages where users.uID = usercon.uID and usercon.cID = conmess.cID and conmess.mID = messages.mID and users.uID = %s"
values = [st.session_state.uID]
cursor.execute(query,values)

rows = cursor.fetchall()

selection = []
for row in rows:
    if(row[0] is None):
        continue
    selection.append(row[0])

#Trend to follow
trend = st.selectbox("Trend to Follow",selection)
#Update trend
if(trend!=st.session_state.trend):
    st.session_state.trend = trend
    st.rerun()

option = 0
#Curve is smooth or not
if st.checkbox("📈 Linear (May be more accurate)"):
    option = 1
else:
    option = 0


if(option != st.session_state.linear):
    st.session_state.linear = option
    st.rerun()

k = 2
if(st.session_state.linear == 1):
    k =1
else:
    k=3

#Get graph
query = "SELECT count(*),conversations.lastInteraction from users,usercon,conversations,conmess,messages where users.uID = usercon.uID and usercon.cID =conversations.cID and conversations.CID = conmess.cID and conmess.mID = messages.mID and users.uID = %s and sentiment=%s group by conversations.cID order by conversations.lastInteraction;"
values = [st.session_state.uID,st.session_state.trend]
cursor.execute(query,values)
x = []
y = []
i=0
for row in cursor.fetchall():
    y.append(row[0])
    x.append(row[1])
    i+=1

x=pd.to_datetime(x)
y = np.array(y)

if len(x)>3:
    x_numeric  = x.view('int64')//10**9 #Convert date to numeric
    spl = make_interp_spline(x_numeric,y,k)
    x_smooth_numeric = np.linspace(x_numeric.min(),x_numeric.max(),50)
    y_smooth = spl(x_smooth_numeric)
    x_smooth = pd.to_datetime(x_smooth_numeric,unit='s') #Convert back to datetime
    
    #Clip y values
    y_smooth = np.clip(y_smooth,0,np.max(y_smooth))
    
    #Normalize y smooth
    y_smooth_min,y_smooth_max = np.min(y_smooth),np.max(y_smooth)
    y_smooth = (((y_smooth - y_smooth_min))/(y_smooth_max-y_smooth_min))*np.max(y)

else:
    x_smooth,y_smooth = x,y



#Draw the plot
fig,ax = plt.subplots()
ax.plot(x_smooth,y_smooth,color="red")
ax.fill_between(x_smooth, y_smooth, alpha=0.3, color='red')
#Reduce font size
ax.tick_params(axis='x', rotation=45, labelsize=8)  # Decrease font size
ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%b %d'))  # Format as "Date Day"



ax.set_xlabel("Date")
ax.set_ylabel("Frequency")
st.pyplot(fig)