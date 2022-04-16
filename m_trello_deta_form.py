import streamlit as st
import pandas as pd
import numpy as np

from datetime import datetime
from deta import Deta
import json
import requests
import base64




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
        enter = st.form_submit_button("Enter")
        if enter :
            items.append(line)
            st.write(items)
            st.session_state['items'] = items
            st.dataframe(items)
            if last == "Yes" :
                st.session_state['more'] = "No"
                del st.session_state['items']

                del st.session_state['more']

if 'more' in st.session_state:
    pass
else:
    st.header("Create and Order")
    with st.form("Create Order Card", clear_on_submit=True):

        cfd = {}
        #changed to requests
        res_get = requests.get('https://bpqc1s.deta.dev/get_definitions?board_id={}'.format("61120a2d004a725ed3f7f0db")) #st.write("slider", slider_val, "checkbox", checkbox_val)
        cfd = res_get.json()['cfd']
        collect = {}
        collect['board_id'] ="61120a2d004a725ed3f7f0db"
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
            st.write("Creating a card....")
            st.json(collect)
            res_update = requests.post('https://bpqc1s.deta.dev/update', json=collect)
            if res_update.status_code == 200:
            #st.session_state['card_id'] = res_update.json()['card_id']
                st.write("Creating a order lines in Deta....")
                order.put({"line_items" : items}, res_update.json()['card_id'], expire_in = 60)

            else:
                st.error(res_update.text)
