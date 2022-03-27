import streamlit as st
import pandas as pd
import numpy as np

from datetime import datetime
from deta import Deta
import json
import httpx

res = httpx.post('https://70297.wayscript.io/function5')
cfd = res.json()['cfd']
collect = {}

with st.form("Trello Dynamic Custom Field Form"):
    st.write("Inside the form")
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

    # Every form must have a submit button.
    submitted = st.form_submit_button("Submit")
    if submitted:
        st.json(collect)
        #st.write("slider", slider_val, "checkbox", checkbox_val)

st.write("Outside the form")
st.camera_input('Test Camera')
