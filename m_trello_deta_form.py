import streamlit as st
import pandas as pd
import numpy as np

from datetime import datetime
from deta import Deta
import json
import requests
import base64
board_id = st.sidebar.selectbox(
    "Select a board",
    ("5fdd53039a97d380e792101e", "5fdd5958823f7d04004f236f", "61120a2d004a725ed3f7f0db")
)

order = Deta("c0vidk60_8unssenvnHkuZmQfqhZ4jW49o5hRMvwG").Base("trello_orders")
if 'more' in st.session_state :
    pass
else:
    st.session_state['more'] = "Yes"


if 'items' in st.session_state :
    pass
else:
    st.session_state['items'] = []
last_line = 0
items = st.session_state['items']
st.write(items)
if st.session_state['more'] == "Yes" :
    form_name = "Order Line Items {}".format(last_line)
    with st.form(form_name, clear_on_submit=True):
        line = {}
        line['collar'] = st.selectbox("Collar", ("Round", "V-shaped"))
        line['size'] = st.selectbox("Size", ("Extra Large", "Large", "Medium", "Small"))
        line['quantity'] = st.number_input("Quantity", min_value=1)
        line['remarks'] = st.text_input(label="Remarks")
        last = st.selectbox("Last Item", ("No", "Yes"))


        line['sno'] = len(items) + 1
        last_line = line['sno']
        create = st.form_submit_button("Create")
        if create :
            items.append(line)
            st.write(items)
            st.session_state['items'] = items
            st.dataframe(items)
            if last == "Yes" :
                st.session_state['more'] = "No"
                del st.session_state['items']
st.header("Create a card")
del st.session_state['more']
st.text_input("Card Name")
st.text_area("Card Description")
