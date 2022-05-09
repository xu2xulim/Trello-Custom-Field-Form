import streamlit as st
import pandas as pd
import numpy as np

from datetime import datetime
import pytz
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

        if option:
            st.write('You selected:', option)
            st.write("Also what section do you need for your form. The default is All sections.")


            if 'sections' not in st.session_state:
                skip = st.button("Skip")
                if skip:
                    st.session_state['sections'] = ['Description with Markdown', 'Start and or Due Dates', 'Labels and more', 'Checklists', 'Custom Fields', 'Attachments']

                with st.expander("Customise the form sections you need. The default is ALL."):

                    with st.form("Form Sections", clear_on_submit=True):
                        sections = st.multiselect("Selection the sections for the form:", ['Description with Markdown', 'Start and or Due Dates', 'Labels and more', 'Checklists', 'Custom Fields', 'Attachments'], ['Description with Markdown', 'Start and or Due Dates', 'Labels and more', 'Checklists', 'Custom Fields', 'Attachments'])
                        create = st.form_submit_button("Create Form")

                        if create:
                            st.session_state['sections'] = sections
                            st.experimental_rerun()
            else:
                st.write("The following sections had been selected: {}".format(st.session_state['sections']))

        st.session_state['board_id'] = board_dict[option]
        st.write(st.session_state)
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



if not st.session_state['authentication_status'] or 'sections' not in st.session_state :
    st.stop()

### Authentication Ends Here....
order = Deta(st.secrets["DETA_PROJECT_ID"]).Base("trello_orders")
st.header("Trello Form with Streamlit")
st.info("This is a fully user configurable form to create Trello Cards. The options and fields are dynamically created based on the board definitions. This include custom fields, labels, list names, members ..etc")

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

if st.session_state['focus'] == 1 :
    if 'desc' not in st.session_state:
        st.session_state['desc'] = ""

    with st.expander("Open to create your card."):
        st.info("You have indicated that you will be using Markdown in your card description.")
        st.warning("When you are satisfied pressed the Finished button to create the card.")
        finished = st.button("Finished")
        if finished:
            st.session_state['focus'] = 1.5
            st.experimental_rerun()

        if 'Description with Markdown' in st.session_state['sections']:

            with st.empty():
                desc_md = st.markdown(st.session_state['desc'])

            with st.form("Card Markdown", clear_on_submit=False):

                desc = st.text_area('Card Description', value = st.session_state['desc'])

                review = st.form_submit_button("Review Markdown")

                if review :
                    st.session_state['desc'] = desc
                    st.experimental_rerun()
        else:
            st.session_state['focus'] = 1.5


if st.session_state['focus'] ==1.5:
    with st.form("Create Card", clear_on_submit=True):
        collect = {}
        collect['board_id'] =st.session_state['board_id']
        collect['cardname'] = st.text_input('Card Name')
        collect['carddescription'] = st.text_area('Card Description', value = st.session_state['desc'])
        create_trello_card = st.form_submit_button("Create Card")

        if create_trello_card:
            st.write("Creating card...")
            res_create_card = requests.post('https://bpqc1s.deta.dev/add_card', json=collect)
            if res_create_card.status_code == 200:
                st.session_state['card_id'] = res_create_card.json()['card_id']
                if 'Labels and more' in st.session_state['sections'] or 'Checklists' in st.session_state['sections']:
                    res_get = requests.post('https://bpqc1s.deta.dev/get_more', json = {"card_id" : st.session_state['card_id'] }) #st.write("slider", slider_val, "checkbox", checkbox_val)
                    st.session_state['more_cfd'] = res_get.json()['more']
                st.session_state['focus'] = 2
                st.experimental_rerun()
            else:
                st.write("Failed to Create Card")
                st.stop()

if st.session_state['focus'] == 2 and 'Start and or Due Dates' in st.session_state['sections'] :

    with st.expander("Open to enter Start and or Due Dates."):

        with st.form("Enter Start and Due Dates", clear_on_submit=True):
            collect={}
            collect['card_id'] = st.session_state['card_id']
            collect['start_date'] = st.date_input("Enter Start Date").strftime("%Y-%m-%d")
            due_dt = st.date_input("Enter Due Date")
            due_tm = st.time_input("Enter Due Date - time")
            collect['due_date'] = "{}T{}".format(due_dt,due_tm)

            submit = st.form_submit_button("Submit")

            if submit:
                st.write('Updating card....')
                st.json(collect)
                res_dates = requests.post('https://bpqc1s.deta.dev/update_card_dates', json = collect)
                if res_dates.status_code == 200 :
                    st.session_state['focus'] = 3
                    st.experimental_rerun()
                else:
                    st.warning("Update card start and due dates failed")
                    st.stop()

if st.session_state['focus'] == 3 :

    if 'Custom Fields' in st.session_state['sections'] :
        with st.expander("Open to enter the data for the custom fields on the card."):

            cfd = {}
            res_get = requests.get('https://bpqc1s.deta.dev/get_definitions?board_id={}'.format(st.session_state['board_id'])) #st.write("slider", slider_val, "checkbox", checkbox_val)
            cfd = res_get.json()['cfd']
            with st.form("Enter the custom field data", clear_on_submit=True):
                collect = {}
                collect['board_id'] =st.session_state['board_id']
                collect['card_id'] = st.session_state['card_id']
                #collect['carddescription'] = st.text_area('Card Description')
                st.warning("This section of the form is automatically generated.")
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

                submit = st.form_submit_button("Submit")

                if submit:
                    st.write('Updating card....')
                    st.json(collect)
                    res_set = requests.post('https://bpqc1s.deta.dev/set_customfields', json=collect)
                    if res_set.status_code == 200 :
                        st.session_state['focus'] = 4
                        st.experimental_rerun()
                    else:
                        st.warning("Something is wrong with setting CFs")
                        st.stop()
    else:
        st.session_state['focus'] = 4
        st.experimental_rerun()

if st.session_state['focus'] == 4 :
    if 'Attachments' in st.session_state['sections']:
        with st.expander("Open to upload attachments"):
            uploaded_file = st.file_uploader('Upload any file up to 200MB')
            finished = st.button("Done")
            attach = {}
            if finished :
                st.session_state['focus'] = 5
                st.experimental_rerun()
            else:
                if uploaded_file is not None:
                    st.write('Updating card....')
                    bytes_data = uploaded_file.getvalue()
                    attach['card_id'] = st.session_state['card_id']
                    attach['filename'] = uploaded_file.name
                    res_attach = requests.post('https://bpqc1s.deta.dev/attach', data=attach, files = {'upload_file': bytes_data})
    else:
        st.session_state['focus'] = 5
        st.experimental_rerun()

if st.session_state['focus'] == 5 :
    if 'Checklists' in st.session_state['sections']:

        with st.expander("Open to create your checklist items."):
            st.warning("Use the done button when you have no more Checklist to add.")
            done = st.button("Done")
            if done:
                st.session_state['focus'] = 6
                st.experimental_rerun()

            st.info("Use the Finished button when you have no more items to add.")
            finished = st.button("Finished")
            if finished:
                st.session_state['focus'] = 5.5
                st.session_state['more'] = "No"
                st.experimental_rerun()

            items = st.session_state['items']
            if st.session_state['more'] == "Yes" :
                st.subheader("Your items :")
                st.dataframe(items)
                st.subheader("Create Line Items")
                form_name = "Line Items {}".format(len(items))
                with st.form(form_name, clear_on_submit=True):
                    line = {}
                    line['name'] = st.text_input("Item Name")
                    due = st.date_input("Enter Item Due Date")
                    line['due'] = due.strftime("%Y-%m-%d")
                    line['member'] = st.selectbox("Select Assigned Member", options=list(st.session_state['more_cfd']['members'].keys()))

                    enter = st.form_submit_button("Enter")
                    if enter :
                        items.append(line)
                        st.session_state['items'] = items
                        st.experimental_rerun()
    else:
        st.session_state['focus'] = 6
        st.experimental_rerun()

if st.session_state['focus'] ==5.5:
    with st.expander("Open if you need to remove any line items"):
        items = st.session_state['items']
        max_index = len(items) - 1
        st.subheader("Your items :")
        st.dataframe(items)
        with st.form("Pick the record by its index to remove",clear_on_submit=True):
            del_index = st.number_input("Index", min_value=0, max_value=max_index, step=1)
            delete = st.form_submit_button("Delete")
            add_more = st.form_submit_button("Add More")

            if delete :
                del items[del_index]
                st.session_state['items'] = items
                st.experimental_rerun()

            if add_more:
                st.session_state['focus'] = 5
                st.session_state['more'] = "Yes"
                st.experimental_rerun()

    with st.expander("Create Checklist"):

        with st.form("Review and create checklist",clear_on_submit=True):
            st.dataframe(st.session_state['items'])

            collect= {}
            collect['card_id'] = st.session_state['card_id']
            collect['checklistname'] = st.text_input("Enter checklist name")
            collect['items'] = st.session_state['items']
            submit = st.form_submit_button("Submit")

            if submit:
                st.write('Updating card....')
                res_add = requests.post('https://bpqc1s.deta.dev/add_checklist', json=collect)
                if res_add.status_code == 200:
                    st.session_state['items'] = []
                    st.session_state['focus'] = 5
                    st.session_state['more'] = "Yes"
                    st.experimental_rerun()
                else:
                    st.warning("Add Checklist Failed")
                    st.stop()


if st.session_state['focus'] == 6 :
    if 'Labels and more' in st.session_state['sections']:
        with st.expander("Open to add labels, members or move to another list"):
            #res_get = requests.post('https://bpqc1s.deta.dev/get_more', json = {"card_id" : st.session_state['card_id'] }) #st.write("slider", slider_val, "checkbox", checkbox_val)
            #cfd = res_get.json()['more']
            with st.form("Add more stuff", clear_on_submit=True):
                st.subheader("Add labels, members to card")
                labels = st.multiselect("Pick the labels to add to the card", list(st.session_state['more_cfd']['labels'].keys()))
                members = st.multiselect("Pick the members to add to the card",list(st.session_state['more_cfd']['members'].keys()))
                column = st.selectbox("Select the list to move the card",list(st.session_state['more_cfd']['lists'].keys()))

                no_more = st.form_submit_button("Submit")

                if no_more :
                    return_struct = {}
                    return_struct['labels'] = []
                    for lbl in labels :
                        return_struct['labels'].append(st.session_state['more_cfd']['labels'][lbl])
                    return_struct['members'] = []
                    for mbr in members :
                        return_struct['members'].append(st.session_state['more_cfd']['members'][mbr])
                    if column :
                        return_struct['move'] = st.session_state['more_cfd']['lists'][column]
                    st.write('Updating card....')
                    res_update = requests.post('https://bpqc1s.deta.dev/update_card', json = {"card_id" : st.session_state['card_id'], "more" : return_struct })

                    if res_update.status_code == 200:
                        del st.session_state['more']
                        del st.session_state['items']
                        del st.session_state['card_id']
                        del st.session_state['more_cfd']
                        del st.session_state['desc']
                        st.session_state['focus'] = 1
                        st.experimental_rerun()
                    else:
                        st.write(res_update.text)
    else:
        del st.session_state['more']
        del st.session_state['items']
        del st.session_state['card_id']
        del st.session_state['more_cfd']
        del st.session_state['desc']
        st.session_state['focus'] = 1
        st.experimental_rerun()
