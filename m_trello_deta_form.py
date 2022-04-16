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
cfd = {}
card_id = None
st.title("Trello Dynamic Custom Field Form")
#changed to requests
res_get = requests.get('https://bpqc1s.deta.dev/get_definitions?board_id={}'.format(board_id)) #st.write("slider", slider_val, "checkbox", checkbox_val)
cfd = res_get.json()['cfd']


with st.form("Trello Order with Deta", clear_on_submit=True):
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
            st.session_state['card_id'] = res_update.json()['card_id']
            card_id = res_update.json()['card_id']
            order.put({"line_items" : []},card_id)
        else:
            st.error(res_update.text)


st.header("You can now add order items to be stored in Deta Base")
if card_id != None :
    items = []
    last_order = 0
    res = order.get(card_id)
    st.write(res)

    if res['line_items'] != None :
        items = res['line_items']
        last_order = len(items)

        more = "Yes"
        while more == "Yes" and ready !=None :
            with st.form("Order Details", clear_on_submit=True):
                line = {}
                col1, col2, col3, col4, col5= st.columns(5)
                line['collar'] = col1.selectbox("Collar", ("Round", "V-shaped"))
                line['size'] = col2.selectbox("Size", ("Extra Large", "Large", "Medium", "Small"))
                line['quantity'] = col3.number_input("Quantity", min_value=1)
                line['remarks'] = col4.text_input(label="Remarks")
                more = col5.selectbox("Last Item", ("No", "Yes"))

                line['sno'] = last_order + 1
                items.append(line)

                create = st.form_submit_button("Create")

                if create :
                    st.write(line)
                    st.write(items)
                    st.write(ready)
                    update_base = order.put({"line_items" : items}, card_id)
                    st.write(update_base)
                    if more == "No" :
                        ready = None
