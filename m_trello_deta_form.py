import streamlit as st
import pandas as pd
import numpy as np

from datetime import datetime
from deta import Deta
import json
import requests
import base64

order = Deta(st.secrets["DETA_PROJECT_ID"]).Base("trello_orders")
st.header("Trello Order with Deta")

if 'focus' in st.session_state:
    if st.session_state == 1 :
        for key in st.session_state :
            del st.session_state[key]

if 'more' in st.session_state :
    pass
else:
    st.session_state['more'] = "Yes"

if 'items' in st.session_state :
    pass
else:
    st.session_state['items'] = []

if 'focus' in st.session_state:
    pass
else:
    st.session_state['focus'] = 1

if st.session_state['focus'] == 2 :
    st.subheader("Your items :")
    st.dataframe(st.session_state['items'])

if st.session_state['focus'] == 1:
    with st.expander("Open to enter order details"):
        #last_line = 0
        items = st.session_state['items']
        last = "No"
        if st.session_state['more'] == "Yes" :
            st.subheader("Your items :")
            st.dataframe(items)
            st.subheader("Create Line Items")
            form_name = "Order Line Items {}".format(len(items))
            with st.form(form_name, clear_on_submit=True):
                line = {}
                line['collar'] = st.selectbox("Collar", ("Round", "V-shaped"))
                line['size'] = st.selectbox("Size", ("Extra Large", "Large", "Medium", "Small"))
                line['quantity'] = st.number_input("Quantity", min_value=1)
                line['remarks'] = st.text_input(label="Remarks")
                last = st.selectbox("Last Item", ("No", "Yes"))
                #last_line = len(items) + 1
                enter = st.form_submit_button("Enter")
                if enter :
                    items.append(line)
                    st.session_state['items'] = items
                    st.write("just before if check")
                    st.write(last)
                    if last == "Yes" :
                        st.write("just after if check")
                        st.session_state['more'] = "No"
                        st.write(st.session_state)
                        st.session_state['focus'] = 2
                    st.experimental_rerun()

if st.session_state['focus'] == 2 :
    with st.expander("Open if you need to remove any line items"):
        items = st.session_state['items']
        max_index = len(items) - 1
        with st.form("Pick the record by its index to remove",clear_on_submit=True):
            st.number_input("Index", min_value=0, max_value=max_index, step=1)
            del_index = st.form_submit_button("Delete")
            add_more = st.form_submit_button("Add More")

            if del_index :
                del items[del_index]
                st.session_state['items'] = items
                st.experimental_rerun()

            if add_more:
                st.session_state['focus'] = 1
                st.session_state['more'] = "Yes"
                st.experimental_rerun()

if st.session_state['focus'] == 2 :
    with st.expander("Open to create order card"):
        items = st.session_state['items']
        with st.form("Create Order Card", clear_on_submit=True):
            st.subheader("Create an Order Card")
            cfd = {}
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

            ready = st.form_submit_button("Submit")

            if ready:
                st.write("Creating a card....")
                #st.dataframe(items)
                #st.json(collect)
                #st.write(st.session_state)
                res_update = requests.post('https://bpqc1s.deta.dev/update', json=collect)
                if res_update.status_code == 200:
                    st.write("Creating a order lines in Deta....")
                    st.session_state['card_id'] = res_update.json()['card_id']
                    order.put({"line_items" : items}, res_update.json()['card_id'])
                    st.write("Finishing cleaning up.....")
                    st.session_state['focus'] = 3
                    st.experimental_rerun()
                else:
                    st.error(res_update.text)

if st.session_state['focus'] == 3 :
    with st.expander("Open to upload samples"):
        uploaded_file = st.file_uploader('Upload any file up to 200MB')
        finished = st.button("Done")
        attach = {}
        if finished :
            #for key in st.session_state :
                #del st.session_state[key]
            st.session_state['focus'] = 1
            st.experimental_rerun()
        else:
            if uploaded_file is not None:
                bytes_data = uploaded_file.getvalue()
                attach['card_id'] = st.session_state['card_id']
                attach['filename'] = uploaded_file.name
                res_attach = requests.post('https://bpqc1s.deta.dev/attach', data=attach, files = {'upload_file': bytes_data})

if st.session_state['focus'] == 3 :
    with st.expander("Open to add labels, members or move to another list"):
        res_get = requests.post('https://bpqc1s.deta.dev/get_more', json = {"card_id" : st.session_state['card_id'] }) #st.write("slider", slider_val, "checkbox", checkbox_val)
        cfd = res_get.json()['more']
        st.write(cfd)
        with st.form("Add more stuff", clear_on_submit=True):
            st.subheader("Add more to card")
            labels = st.multiselect("Pick the labels to add to card", [k for k, v in cfd['labels']])
            st.write('You selected:', labels)
            members = st.multiselect("Pick the members to add to card", [k for k, v in cfd['members']])
            st.write('You selected:', members)

            no_more = st.button("Done")
            attach = {}
            if no_more :
                return_struct = {}
                inv_labels = {v: k for k, v in cfd['labels'].items()}
                return_struct['labels'] = []
                for lbl in labels :
                    return_struct['labels'].append(inv_labels(lbl))
                inv_memberss = {v: k for k, v in cfd['members'].items()}
                return_struct['members'] = []
                for lbl in labels :
                    return_struct['members'].append(inv_members(lbl))
                st.write(return_struct)
                st.write('Updating card....')
                #for key in st.session_state :
                    #del st.session_state[key]
                st.session_state['focus'] = 1
                st.experimental_rerun()
