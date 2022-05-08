import streamlit as st
import pandas as pd
import numpy as np

from datetime import datetime
from deta import Deta
import json
import requests
import base64
### Authentication Starts Here....
import urllib.request
import urllib.parse
import os
import streamlit.components.v1 as components
import streamlit_authenticator as stauth

Users=Deta(os.environ.get('DETA_PROJECT_ID')).Base(os.environ.get('MILYNNUS_ST_USERS_BASE'))

@st.cache(suppress_st_warning=True)
def get_board_json (urls):
    payload = {"board_urls" : urls }
    res_options = requests.post('https://bpqc1s.deta.dev/get_options', json=payload)
    if res_options.status_code == 200 :
        return res_options.json()
    else:
        return {}
    return board_json

@st.cache(suppress_st_warning=True)
def auth_init():

    res = Users.fetch(query=None, limit=100, last=None)
    names = []
    usernames = []
    hashed_passwords = []
    for x in res.items :
        names.append(x['name'])
        usernames.append(x['username'])
        hashed_passwords.append(x['hash_password'])

    return names, usernames, hashed_passwords

with st.sidebar:
    st.title("Trello Form With Streamlit")
    names, usernames, hashed_passwords = auth_init()

    st.info("This application is secured by Streamlit-Authenticator.")
    authenticator = stauth.Authenticate(names, usernames, hashed_passwords,
        'milynnus_stauth', os.environ.get('MILYNNUS_ST_USERS_SIGNATURE'), cookie_expiry_days=30)

    name, authentication_status, username = authenticator.login('Login', 'sidebar')
    #st.info(st.session_state)
    if st.session_state['authentication_status']:
        authenticator.logout('Logout', 'main')
        st.write('Welcome *%s*' % (st.session_state['name']))

        res = Users.fetch(query={"name" : name, "username" : username}, limit=None, last=None)
        if len(res.items) == 1:
            user = Users.get(res.items[0]["key"])

            if "cf_form_boards" in user.keys():
                board_dict = get_board_json(user["cf_form_boards"])

        option = st.selectbox(
            'Select the board you are using',
            options=list(board_dict.keys()))

        st.write('You selected:', option)
        st.session_state['board_id'] = board_dict[option]
    elif st.session_state['authentication_status'] == False:
        st.error('Username/password is incorrect')
    elif st.session_state['authentication_status'] == None:
        if 'board_id' in st.session_state:
            del st.session_state['board_id']
        st.warning('Please enter your username and password')

    if not st.session_state['authentication_status']:
        with st.expander("Register"):
            st.warning("This form is for user self registration. The registration data is kept in a Deta Base.")
            with st.form("Fill in your name, your preferred username and password", clear_on_submit=True):
                name = st.text_input("Name")
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                username_unique = Users.fetch(query={"username" : username})
                submit = st.form_submit_button("Submit")
                if username_unique.count == 0:
                    pass
                else:
                    st.write("The username : {} has been used, please use another preferred username.".format(username))
                    st.stop()

                if submit:
                    Users.put({'name' : name, 'username' : username, 'hash_password' : stauth.Hasher([password]).generate()[0]})

        with st.expander("Admin setup"):
            st.warning("This form is used by the administrator to attach card urls to a username. An admin secret is required for the update.")
            with st.form("Enter the card url to be shared with the user", clear_on_submit=True):
                username = st.text_input("Username")
                url = st.text_input("Board URL")
                admin_secret = st.text_input("Admin Secret", type="password")

                submit = st.form_submit_button("Submit")

                if submit and admin_secret == os.environ.get('MILYNNUS_ST_USERS_SIGNATURE'):
                    users = Users.fetch(query={"username" : username}, limit=None, last=None)
                    if len(users.items) != 1 :
                        st.write("User is not found")
                    else:
                        st.write(users.items[0]["key"])
                        user = Users.get(users.items[0]["key"])
                        try :
                            form_boards = user['cf_form_boards']
                        except:
                            form_boards = []

                        if url in form_boards :
                            st.write("Board with url {} can be used by this app by {}".format(url, username))
                        else:
                            form_boards.append(url)
                            Users.update({"cf_form_boards" : form_boards }, user["key"])
                            st.write("Board with url {} can now be used by this app by {}".format(url, username))



if not st.session_state['authentication_status']  :
    st.stop()

### Authentication Ends Here....
order = Deta(st.secrets["DETA_PROJECT_ID"]).Base("trello_orders")
st.header("Trello Form With Streamlit")
st.write("Start by customising the sections you need for your form. The default is All sections.")
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

if st.session_state['focus'] == 0:
    skip = st.button("Skip")
    if skip:
        st.session_state['sections'] = ['All']
        st.session_state['focus'] == 1
        st.experimental_rerun()

    with st.expander("Customise the form sections you need. The default is ALL."):

        with st.form("Form Sections", clear_on_submit=True):
            sections = st.multiselect("Selection the sections for the form:", ['Description with Markdown', 'Start and or Due Dates', 'Labels', 'Checklists', 'Custom Fields', 'Attachments'], ['Custom Fields'])
            create = st.form_submit_button("Create Form")

            if create:
                st.session_state['sections'] = sections
                st.session_state['focus'] == 1
                st.experimental_rerun()


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
            res_get = requests.get('https://bpqc1s.deta.dev/get_definitions?board_id={}'.format(st.session_state['board_id'])) #st.write("slider", slider_val, "checkbox", checkbox_val)
            cfd = res_get.json()['cfd']
            collect = {}
            collect['board_id'] =st.session_state['board_id']
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
                    st.session_state['card_url'] = res_update.json()['card_shortUrl']
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
            st.session_state['focus'] = 4
            st.experimental_rerun()
        else:
            if uploaded_file is not None:
                bytes_data = uploaded_file.getvalue()
                attach['card_id'] = st.session_state['card_id']
                attach['filename'] = uploaded_file.name
                res_attach = requests.post('https://bpqc1s.deta.dev/attach', data=attach, files = {'upload_file': bytes_data})

if st.session_state['focus'] == 4 :
    components.html('''<blockquote class="trello-card-compact"><a href="'''+st.session_state['card_url']+'''">Trello Card</a></blockquote><script src="https://p.trellocdn.com/embed.min.js"></script>)''')
    with st.expander("Open to add labels, members or move to another list"):
        res_get = requests.post('https://bpqc1s.deta.dev/get_more', json = {"card_id" : st.session_state['card_id'] }) #st.write("slider", slider_val, "checkbox", checkbox_val)
        cfd = res_get.json()['more']
        with st.form("Add more stuff", clear_on_submit=True):
            st.subheader("Add labels, members to card")
            labels = st.multiselect("Pick the labels to add to the card", list(cfd['labels'].keys()))
            members = st.multiselect("Pick the members to add to the card",list(cfd['members'].keys()))
            column = st.selectbox("Select the list to move the card",list(cfd['lists'].keys()))

            no_more = st.form_submit_button("Submit")

            if no_more :
                return_struct = {}
                return_struct['labels'] = []
                for lbl in labels :
                    return_struct['labels'].append(cfd['labels'][lbl])
                return_struct['members'] = []
                for mbr in members :
                    return_struct['members'].append(cfd['members'][mbr])
                if column :
                    return_struct['move'] = cfd['lists'][column]
                st.write('Updating card....')
                res_update = requests.post('https://bpqc1s.deta.dev/update_card', json = {"card_id" : st.session_state['card_id'], "more" : return_struct })

                if res_update.status_code == 200:
                    del st.session_state['more']
                    del st.session_state['items']
                    del st.session_state['card_id']
                    del st.session_state['card_url']
                    st.session_state['focus'] = 1
                    st.experimental_rerun()
                else:
                    st.write(res_update.text)
