import streamlit as st
import pandas as pd
import numpy as np

from datetime import datetime
from deta import Deta
import json
import httpx

res = httpx.post('https://70297.wayscript.io/function5')
cfd = res.json()['cfd']
st.write(cfd)
