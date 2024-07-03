import streamlit as st
import pandas as pd
import numpy as np

import requests
import json

st.set_page_config(page_title="Test", layout='wide')

#df = pd.DataFrame(np.random.randn(10, 20), columns=("col %d" % i for i in range(20)))
#st.dataframe(df.style.highlight_max(axis=0))

url1 = 'https://raw.githubusercontent.com/insightbuilder/python_de_learners_data/main/code_script_notebooks/python_scripts/json_reader/toplevel_comment_zGAkhN1YZXM.json'
url2 = 'https://www.hatvp.fr/agora/opendata/agora_repertoire_opendata.json'
url3 = 'https://api.gouv.fr/api/v1/apis'

response = requests.get(url3).json()
#st.dataframe(response)

st.write("Start FOR")
for element in response: 
  for value in response['logo']:  #response['Name_OF_YOUR_KEY/ELEMENT']:
    st.write(response['logo'][0'])   #print(response['Name_OF_YOUR_KEY/ELEMENT']['INDEX_OF_VALUE']['VALUE'])
st.write("End FOR")
             
st.dataframe(
  data=response, 
  #width=None, 
  #height=None, 
  #*, 
  use_container_width=True, 
  hide_index=None, 
  column_order=None, 
  #column_config=None, 
  column_config={
    "logo": st.column_config.ImageColumn( "Logo", help="API's logo" ),
    "datapass_link": st.column_config.LinkColumn( "URL", help="Official link" )
  },  
  key=None, 
  on_select="ignore", 
  selection_mode="multi-row")
