import streamlit as st
import pandas as pd
import numpy as np

from datetime import datetime
from deta import Deta
import json
import requests
board_id = st.sidebar.selectbox(
    "Select a board",
    ("5fdd53039a97d380e792101e", "5fdd5958823f7d04004f236f")
)
cfd = {}
st.title("Trello Dynamic Custom Field Form")
#changed to requests
res_get = requests.get('https://bpqc1s.deta.dev/get_definitions?board_id={}'.format(board_id)) #st.write("slider", slider_val, "checkbox", checkbox_val)
cfd = res_get.json()['cfd']


with st.form("Trello Dynamic Custom Field Form", clear_on_submit=True):
    collect = {}
    collect['board_id'] = board_id
    collect['cardname'] = st.text_input('Card Name')
    collect['carddescription'] = st.text_area('Card Description')
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
            collect[df['name']] = round(st.number_input(df['name'],step=0.1), 2)
            # Every form must have a submit button.

    ready = st.form_submit_button("Submit")

    if ready:
        st.json(collect)
        res_update = requests.post('https://bpqc1s.deta.dev/update', json=collect)
        if res_update.status_code == 200:
            card_id = res_update.json()['card_id']
            st.balloons()
        else:
            st.error(res_update.text)


st.write("Outside the form")
st.header('Above is the json output generated')
uploaded_file = st.file_uploader('Upload any file up to 200MB')
attach = {}
if uploaded_file is not None:
     # To read file as bytes:
     attach['card_id'] = card_id
     attach['bytes_data'] = uploaded_file.getvalue()
     res_attach = requests.post('https://bpqc1s.deta.dev/attach', json=attach)

"""
st.header('You can incorporate other cool things like')
st.camera_input('Test Camera')

st.color_picker('Pick a color')
st.write('Please note that this is demo and the data is not capture in Trello')

"""
