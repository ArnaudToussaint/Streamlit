import streamlit as st
import pandas as pd
import numpy as np

import requests
import json


df = pd.DataFrame(np.random.randn(10, 20), columns=("col %d" % i for i in range(20)))

st.dataframe(df.style.highlight_max(axis=0))

data = requests.get("'https://jsonplaceholder.typicode.com/todos/1'").json()
#https://www.hatvp.fr/agora/opendata/agora_repertoire_opendata.json
st.write(data)
