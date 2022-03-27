import streamlit as st
import pandas as pd
import numpy as np

from datetime import datetime
from deta import Deta
import json
import httpx

res = httpx.post('https://70297.wayscript.io/function5')
cfd = res.json()['cfd']
for df in cfd:
    if df['type'] == 'text' :
        st.text_input(df['name'])
    elif df['type'] == 'checkbox' :
        st.checkbox(df['name'], value=False)
    elif df['type'] == 'date' :
        st.date_input("Enter date for {}".format(df['name']))
        st.time_input("Enter time for {}".format(df['name']))
    elif df['type'] == 'list' :
        options = [choice['value']['text'] for choice in df['options']]
        st.selectbox(df['name'], options=options)
