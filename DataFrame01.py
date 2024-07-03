import streamlit as st
import pandas as pd
import numpy as np

import requests
import json


df = pd.DataFrame(np.random.randn(10, 20), columns=("col %d" % i for i in range(20)))

st.dataframe(df.style.highlight_max(axis=0))

#data = requests.get("'https://jsonplaceholder.typicode.com/todos/1'").json()
#st.write(data)

url1 = 'https://raw.githubusercontent.com/insightbuilder/python_de_learners_data/main/code_script_notebooks/python_scripts/json_reader/toplevel_comment_zGAkhN1YZXM.json'
url2 = 'https://www.hatvp.fr/agora/opendata/agora_repertoire_opendata.json'

response = requests.get(url1)

#st.dataframe()
