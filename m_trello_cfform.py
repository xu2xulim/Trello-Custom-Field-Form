import streamlit as st
import pandas as pd
import numpy as np

from datetime import datetime
from deta import Deta
import json

cfd_list = [{"id":"617650db607e3a54190c2dbd","idModel":"5fdd53039a97d380e792101e","modelType":"board","fieldGroup":"8d5ec5b3ea7076b70017422b8f5325d1ceb21a53b9fd06583c44bc5f2b79807f","display":{"cardFront":true},"name":"GT_Parent_Card","pos":163840,"options":[{"id":"61765181b2a32d53fdf0eb38","idCustomField":"617650db607e3a54190c2dbd","value":{"text":"Parent Card 1"},"color":"none","pos":16384},{"id":"617651887152e4480ba9bd13","idCustomField":"617650db607e3a54190c2dbd","value":{"text":"Parent Card 2"},"color":"none","pos":32768}],"type":"list","isSuggestedField":false},{"id":"617650f4b7d10f3794e99188","idModel":"5fdd53039a97d380e792101e","modelType":"board","fieldGroup":"5a04c59f4850b2a8c2328941697a6e738d502c6a2f91e0dc37ba1ff76e572861","display":{"cardFront":true},"name":"CT_Action","pos":180224,"options":[{"id":"617650fc80c8260e2cc6109f","idCustomField":"617650f4b7d10f3794e99188","value":{"text":"Add"},"color":"none","pos":16384},{"id":"61765103877d334b07472a77","idCustomField":"617650f4b7d10f3794e99188","value":{"text":"Delete"},"color":"none","pos":32768},{"id":"6176512b7d814147b8713156","idCustomField":"617650f4b7d10f3794e99188","value":{"text":"Update"},"color":"none","pos":49152},{"id":"622318ae2aad805187ed1e5f","idCustomField":"617650f4b7d10f3794e99188","value":{"text":"Correct"},"color":"red","pos":65536},{"id":"622318e5a1166f5c52bb8a0a","idCustomField":"617650f4b7d10f3794e99188","value":{"text":"Force"},"color":"none","pos":81920}],"type":"list","isSuggestedField":false},{"id":"61765233e98dab19aa89e802","idModel":"5fdd53039a97d380e792101e","modelType":"board","fieldGroup":"13e6dacf3718f0ee1e29f8ade88ee11dfe5958144357f2f414f7f2f74cb94f9a","display":{"cardFront":true},"name":"GT_Param","pos":188416,"options":[{"id":"61765233e98dab19aa89e803","idCustomField":"61765233e98dab19aa89e802","value":{"text":"Checklist"},"color":"none","pos":20480},{"id":"61765233e98dab19aa89e804","idCustomField":"61765233e98dab19aa89e802","value":{"text":"Item"},"color":"none","pos":36864},{"id":"61765233e98dab19aa89e805","idCustomField":"61765233e98dab19aa89e802","value":{"text":"Position"},"color":"none","pos":53248},{"id":"61765233e98dab19aa89e806","idCustomField":"61765233e98dab19aa89e802","value":{"text":"Collection"},"color":"none","pos":69632}],"type":"list","isSuggestedField":false},{"id":"617651eaf8f1248a59060b6b","idModel":"5fdd53039a97d380e792101e","modelType":"board","fieldGroup":"79f3fe87df812d0c4586a9d9eec516b0a97d52c5b1b4b3ee796b156a37593f13","display":{"cardFront":true},"name":"GT_Checklist","pos":196608,"type":"text","isSuggestedField":false},{"id":"61765467c72f610f43e835bd","idModel":"5fdd53039a97d380e792101e","modelType":"board","fieldGroup":"27a0507db9bb10ae7e77624b70670ea4829641e5cccd2956162744d2dc9f1f5f","display":{"cardFront":true},"name":"GT_Item","pos":212992,"type":"text","isSuggestedField":false},{"id":"617b31277ec7508b4adb5b19","idModel":"5fdd53039a97d380e792101e","modelType":"board","fieldGroup":"f3c3181b700f69086a8b8e4fde32bf1937180ef74c0c913b829b2be8521428c8","display":{"cardFront":true},"name":"CF_Date","pos":229376,"type":"date","isSuggestedField":false},{"id":"61e7194c30f16785eb670ce8","idModel":"5fdd53039a97d380e792101e","modelType":"board","fieldGroup":"c3ce1a1d8748fe4e8dcc7a01428e808cf9acbe1229f0831bef9addc7075171be","display":{"cardFront":true},"name":"CF_Number","pos":245760,"type":"number","isSuggestedField":false},{"id":"61e78ac1a23c1d14d07519b1","idModel":"5fdd53039a97d380e792101e","modelType":"board","fieldGroup":"ac9b19c7a0d90b16d64a57b826c6e8a1b35da4503d8522f3e490da7a1e822df6","display":{"cardFront":true},"name":"CF_Checkbox","pos":262144,"type":"checkbox","isSuggestedField":false}]

df = pd.DataFrame(cfd_list)
st.write(df.head())
