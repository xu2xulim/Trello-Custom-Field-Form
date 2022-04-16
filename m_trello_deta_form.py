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
    ("61120a2d004a725ed3f7f0db")
)

order = Deta().Base("trello_orders")
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
            st.session_state['card_id'] = res_update.json()['card_id']
        else:
            st.error(res_update.text)

card_id = st.session_state['card_id']
st.header("You can now add order items to be stored in Deta Base")

items = []
last_order = 0
res = order.get(card_id)
if res['line_items'] != None :
    items = res['line_items']
    last_order = len(items.keys())
st.write(items)

line = {}
col1, col2, col3, col4= st.columns(4)
line['collar'] = col1.download_button(label="Collar", ("Round", "V-shaped"))
line['size'] = col2.selectbox(label="Size", ("Extra Large", "Large", "Medium", "Small"))
line['quantity'] = col3.number_input(label="Quantity", min_value=1, max_value=100, step=1)
line['remarks'] = col4.text_input(label="Remarks")
line['sno'] = len + 1
items.append(line)

update_base = order.put({"line_items" = items}, card_id)
