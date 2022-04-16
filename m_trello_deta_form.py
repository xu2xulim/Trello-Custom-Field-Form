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
if 'more' in st.session.state :
    pass
else:
    st.session.state['more'] = "Yes"

if st.session.state['more'] == "Yes" :
    with st.form("Order Details", clear_on_submit=True):
        line = {}

        line['collar'] = st.selectbox("Collar", ("Round", "V-shaped"))
        line['size'] = st.selectbox("Size", ("Extra Large", "Large", "Medium", "Small"))
        line['quantity'] = st.number_input("Quantity", min_value=1)
        line['remarks'] = st.text_input(label="Remarks")
        last = st.selectbox("Last Item", ("Yes", "No"))

        line['sno'] = last_order + 1
        items.append(line)

        create = st.form_submit_button("Create")

        if create :
            st.write(line)
            #update_base = order.put({"line_items" : items}, card_id)
            st.dataframe(items)
            if last == "Yes" :
                st.session.state['more'] = "No"
