import streamlit as st
import pandas as pd
import numpy as np

from datetime import datetime
from deta import Deta
import json
import httpx

cfd = {}
st.title("Trello Dynamic Custom Field Form and other cool stuff")

with st.form("Configure Trello Dynamic Custom Field Form"):
    st.write("Collect information required to fetch CF definitions")
    board_id = st.selectbox('Board', options=("5fdd5958823f7d04004f236f", "5fdd53039a97d380e792101e"))
    configured = st.form_submit_button("Submit Request")

    if configured:
        #st.json(collect)
        res = httpx.post('https://70297.wayscript.io/function5?board_id={}'.format(board_id))#st.write("slider", slider_val, "checkbox", checkbox_val)
        cfd = res.json()['cfd']
    else:
        cfd = {}


collect = {}
with st.form("Trello Dynamic Custom Field Form"):
    st.write("The form is dynamically created based on the custom field definitions of any Trello Board")
    for df in cfd:
        if df['type'] == 'text' :
            collect[df['name']] = st.text_input(df['name'])
        elif df['type'] == 'checkbox' :
            collect[df['name']] = st.checkbox(df['name'], value=False)
        elif df['type'] == 'date' :
            date = st.date_input("Enter date for {}".format(df['name']))
            time = st.time_input("Enter time for {}".format(df['name']))
            collect[df['name']] = "{}T{}".format(date, time)
        elif df['type'] == 'list' :
            options = [choice['value']['text'] for choice in df['options']]
            collect[df['name']] = st.selectbox(df['name'], options=options)
        elif df['type'] == 'number' :
            collect[df['name']] = st.slider(df['name'])

                    # Every form must have a submit button.
    ready = st.form_submit_button("Submit")

    if ready:
        st.json(collect)
        #st.write("slider", slider_val, "checkbox", checkbox_val)

st.write("Outside the form")
st.header('Above is the json output generated')
st.header('You can incorporate other cool things like')
st.camera_input('Test Camera')
st.file_uploader('Upload any file up to 200MB')
st.color_picker('Pick a color')
st.write('Please note that this is demo and the data is not capture in Trello')
